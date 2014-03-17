"""Widgets are used to perform filtering.
"""

from django.utils.text import capfirst

from datable.core.converters import BooleanConverter
from datable.core.converters import DateValueConverter
from datable.core.converters import DateTimeValueConverter
from datable.core.converters import StringValueConverter

from datable.core.filters import BooleanFilter
from datable.core.filters import DateFilter
from datable.core.filters import DateTimeFilter
from datable.core.filters import StringFilter


Minimum = 'min'

Maximum = 'max'


class Constraints(object):
    """This object defines how to change constraints of JS controls
    in the web UI; currently it is used by DateFilter"""
    def __init__(self, kind, name):
        self.kind = kind
        self.name = name


class Widget:

    label = None
    initialValue = None
    placeholder = None
    constraints = None

    converterClass = None
    converterKwargs = None
    converter = None

    filterClass = None
    filterKwargs = None
    filter = None

    templateName = None

    def __init__(self, name, converter=None, converterKwargs=None,
                 converterField=None, filter=None, filterField=None,
                 filterKwargs=None, label=None, initialValue=None,
                 placeholder=None, constraints=None, storage=None,
                 templateName=None):

        self.name = name
        self.converter = converter
        self.filter = filter

        # Label - used in export data
        if label is not None:
            self.label = label

        if self.label is None:
            self.label = capfirst(self.name.replace("_", " "))

        # HTML5 placeholder
        if placeholder is not None:
            self.placeholder = placeholder

        self.constraints = constraints

        if converterKwargs is not None:
            self.converterKwargs = converterKwargs

        if filterKwargs is not None:
            self.filterKwargs = filterKwargs

        # set converter and filter
        for argument, classVar, classClass, field, kwargs in [
            (converter, 'converter', self.converterClass,
             converterField, self.converterKwargs),
            (filter, 'filter', self.filterClass,
             filterField, self.filterKwargs)]:

            if argument is not None:
                setattr(self, classVar, argument)

            if field is None:
                field = self.name

            if getattr(self, classVar, None) is None:
                if classClass is None:
                    raise Exception(
                        "set %(a)sClass or pass %(a)s parameter" % (
                            dict(a=classVar)))
                kw = kwargs or {}
                setattr(self, classVar, classClass(field, **kw))

        if initialValue is not None:
            self.initialValue = initialValue

        self.initialValue_js = self.converter.valueToJS(self.initialValue)

        self.storage = storage

        if templateName is not None:
            self.templateName = templateName

    def existsIn(self, requestDict):
        """Does this widget exists in the requestDict?
        """
        return self.converter.existsIn(requestDict)

    def exportDescription(self, requestDict):
        """Get export description of this field.
        This is used when rendering a file with export data and we want to
        display a description of filters used in the file"""

        if self.existsIn(requestDict):
            return [self.label, self.converter.valueFromJS(requestDict)]

    def filterQuerySet(self, querySet, requestDict):
        """Perfom filtering, using this widget's value
        """
        if self.existsIn(requestDict):
            value = self.converter.valueFromJS(requestDict)
            return self.filter.filterQuerySet(querySet, value)
        return querySet

    def getName(self):
        return self.name

    def getStorage(self):
        return self.storage


class StringWidget(Widget):
    converterClass = StringValueConverter
    filterClass = StringFilter
    filterKwargs = {'operation': 'contains'}
    templateName = "string"


class DateTimeWidget(Widget):
    converterClass = DateTimeValueConverter
    filterClass = DateTimeFilter
    templateName = "datetime"


class DateWidget(Widget):
    converterClass = DateValueConverter
    filterClass = DateFilter
    templateName = "date"


class BooleanWidget(Widget):
    converterClass = BooleanConverter
    filterClass = BooleanFilter
    templateName = "checkbox"
