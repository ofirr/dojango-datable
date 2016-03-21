from django import template
from django.template.loader import get_template
from django.template.base import VariableDoesNotExist

register = template.Library()

#
# Nodes
#


def templatePath(name):
    return "datable/templatetags/%s.html" % name


def widgetTemplatePath(name):
    return "datable/templatetags/widgets/%s.html" % name


class SimpleNode(template.Node):
    def render(self, context):
        return get_template(self.templateName).render(template.Context({}))


class DatableInitialNode(SimpleNode):
    """Initial Datable node - contains various dojo.require and CSS imports
    """
    templateName = templatePath("init")


class DatablePreloaderNode(SimpleNode):
    templateName = templatePath("preloader")


class BaseDatableNode(template.Node):
    """Base Datable node - a base class for other Datable nodes (single param)
    """

    def __init__(self, table_name):
        self.table_name = template.Variable(table_name)

    def getcontext(self, context):

        try:
            table = self.table_name.resolve(context)
        except VariableDoesNotExist:
            err = "Variable %s not found in context. Perhaps you forgot " \
                  "to pass it to the renderer?" % self.table_name
            raise VariableDoesNotExist(err)

        opts = dict()
        opts['name'] = self.table_name
        opts['objectpath'] = table.objectpath
        opts['widgets'] = table.getStorage().getWidgets()
        opts['fields'] = []

        ds = table.getStorage().defaultSort
        if ds:
            idx = table.getStorage().getColumnIndex(ds[0].getName()) + 1
            if ds[1]:
                idx = 0 - idx
            opts['defaultSort'] = idx

        opts['image_formatter'] = False
        opts['image_formatter_max_width'] = 64
        opts['image_formatter_max_height'] = 48

        opts['href_formatter'] = False

        opts['nosort'] = set()

        for no, column in enumerate(table.storage.getColumns()):

            d = dict(
                name=column.getName(),
                label=column.getLabel(),
                editable='false',
                formatter=column.getFormatter()
                )

            if column.sortable == False:
                opts['nosort'].add(no + 1)

            if column.width is not None:
                if type(column.width) == int:
                    d['width'] = '%ipx' % column.width
                elif type(column.width) == float:
                    d['width'] = '%.0f%%' % column.width
                else:
                    d['width'] = str(column.width)

            opts['fields'].append(d)
        return opts

    def render(self, context):
        return get_template(self.templateName).render(template.Context(self.getcontext(context)))


class BaseDatableNodeTwoParams(BaseDatableNode):
    """Base Datable node - a base class for other Datable nodes (two parameters)
    """
    def __init__(self, table_name, extraparam):
        BaseDatableNode.__init__(self, table_name)
        self.extraparam = extraparam

    def getcontext(self, context):
        opts = BaseDatableNode.getcontext(self, context)
        opts['extraparam'] = self.extraparam
        return opts


class DatableHrefOnClickNode(BaseDatableNode):
    """Include this node as

    {% datable_href_on_click my_datable %}

    to make your datable support clicking on the rows.
    """
    templateName = templatePath("href_on_click")


class DatableDialogOnClickNode(BaseDatableNodeTwoParams):
    """Include this node as

    {% datable_dialog_on_click my_datable function_name%}

    to make your datable support dialogs by clicking on the rows.
    function_name will be called as function_name(row_pk)
    """
    templateName = templatePath("dialog_on_click")


class DatableNode(BaseDatableNode):
    """Include this node as

    {% datable my_datable %}

    to display your datable.
    """
    templateName = templatePath("disp")


class DatableRefreshButtonNode(BaseDatableNode):
    """Include this node as:

    {% datable_refresh_button my_datable %}

    to display a button. Clicking this button will make the datable reload
    the data. You _must_ also include {% datable_refresh_function my_datable %}
    tag in the template.
    """
    templateName = templatePath("refresh_button")


class DatableXLSButtonNode(BaseDatableNode):
    """Include this node as:

    {% datable_xls_button my_datable %}

    to display a button saying 'Export to XLS'. Clicking this button causes
    browser to go to URL ?want_my_datable_xls .
    """
    templateName = templatePath("xls_button")


class DatableCSVButtonNode(DatableXLSButtonNode):
    """See DatableXLSButtonNode
    """
    templateName = templatePath("csv_button")


class DatableClearAllFiltersButtonNode(DatableXLSButtonNode):
    """Clear all filters button
    """
    templateName = templatePath("clear_all_button")


class DatableMenuButtonNode(BaseDatableNode):
    """Button with pop-up menu with options
    """
    templateName = templatePath("menu_button")

#
# Filters
#


class FilterNode(template.Node):
    def __init__(self, table_name, widget_name):
        self.table_name = template.Variable(table_name)
        self.widget_name = widget_name

    def render(self, context):

        try:
            table = self.table_name.resolve(context)
        except VariableDoesNotExist:
            err = "Table named %s not found in context. Perhaps you forgot " \
                  "to pass it to the renderer?" % self.datable_name
            raise VariableDoesNotExist(err)

        widget = table.storage.getWidget(self.widget_name)
        if widget is None:
            raise Exception("There is no widget %s in table %s" \
                            % (self.widget_name, self.table_name))

        opts = dict()
        opts['table'] = table
        opts['widget'] = widget
        opts['widget_id'] = 'w_%s_%s' % (table.name, widget.name)

        templateName = widget.templateName

        return get_template(widgetTemplatePath(
            templateName)).render(template.Context(opts))


def datable_widget(parser, token):
    try:
        tag_name, datable_name, filter_name = token.split_contents()
    except ValueError:
        err = "%r tag requires two arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError(err)
    return FilterNode(datable_name, filter_name)

register.tag('datable_widget', datable_widget)

#
# Tags
#

for tagname, node in [
    ('datable_init', DatableInitialNode),
    ('datable_preloader', DatablePreloaderNode)]:
    register.tag(tagname, lambda parser, token, node=node: node())


def datable_helper(parser, token, fun):
    """This function helps with registering a single-parameter tag.
    """

    try:
        tag_name, datable_name = token.split_contents()
    except ValueError:
        err = "%r tag requires a single argument" % token.contents.split()[0]
        raise template.TemplateSyntaxError(err)
    return fun(datable_name)

##ofir
def alt_datable_helper(parser, token, fun):
    """This function helps with registering a double-parameter tag.
    """

    try:
        tag_name, datable_name, param = token.split_contents()
    except ValueError:
        err = "%r tag requires two arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError(err)
    return fun(datable_name, param)
##end ofir

for tagname, node in [
    ('datable', DatableNode),
    ('datable_href_on_click', DatableHrefOnClickNode),

    ('datable_refresh_button', DatableRefreshButtonNode),
    ('datable_menu_button', DatableMenuButtonNode),
    ('datable_clear_all_filters_button', DatableClearAllFiltersButtonNode),
    ('datable_xls_button', DatableXLSButtonNode),
    ('datable_csv_button', DatableCSVButtonNode)]:
    register.tag(tagname, lambda parser, token, node=node:
        datable_helper(parser, token, node))

for tagname, node in [
    ('datable_dialog_on_click', DatableDialogOnClickNode)]:
    register.tag(tagname, lambda parser, token, node=node:
    alt_datable_helper(parser, token, node))