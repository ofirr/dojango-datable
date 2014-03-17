from django.utils.translation import ugettext as _

from datable.core.filters import NoFilter
from datable.core.filters import IntegerFilter
from datable.core.filters import StringFilter

from datable.core.converters import IntegerConverter
from datable.core.converters import DojoComboValueConverter

from datable.core.serializers import FormatStringSerializer

from datable.web.storage import Storage

from datable.web.columns import StringColumn

from datable.web.widgets import Widget
from datable.web.widgets import StringWidget
from datable.web.widgets import DateTimeWidget
from datable.web.widgets import DateWidget
from datable.web.widgets import Constraints
from datable.web.widgets import Minimum
from datable.web.widgets import Maximum
from datable.web.widgets import BooleanWidget

from datable.web.extra.filters import WholeDayFilter
from datable.web.extra.filters import OlderThanNow


class WholeDayWidget(DateWidget):
    filterClass = WholeDayFilter


class AutocompleteStringWidget(StringWidget):
    templateName = "autocomplete_string"


def DateWidgetMaker(klass, firstop, constraint, secondop):
    def factory(field, placeholder=None, paired=True):
        constraints = None
        if paired:
            constraints = Constraints(
                constraint,
                field + '_' + secondop
            )

        return klass(
            field + "_" + firstop,
            filter=DateTimeWidget.filterClass(
                field=field,
                operation=firstop),
            placeholder=placeholder,
            constraints=constraints)

    return factory

DateGreaterOrEqual = DateWidgetMaker(DateWidget, 'gte', Minimum, 'lte')
DateLessOrEqual = DateWidgetMaker(DateWidget, 'lte', Maximum, 'gte')

DateTimeGreaterOrEqual = DateWidgetMaker(DateTimeWidget, 'gte', Minimum, 'lte')
DateTimeLessOrEqual = DateWidgetMaker(DateTimeWidget, 'lte', Maximum, 'gte')


def ForeignKeyComboBox(name, otherSet, otherField, otherFormat=None,
                       placeholder=None):
    if otherFormat is None:
        otherFormat = "%%(%s)s" % otherField

    return Widget(
        name,
        filter=IntegerFilter(name + "__pk"),
        converter=IntegerConverter(name, min=0),
        templateName="autocomplete_string",
        placeholder=placeholder,
        storage=Storage(
            querySet=otherSet,
            columns=[
                StringColumn(
                    'label',
                    serializer=FormatStringSerializer(otherFormat)),
                ],
            widgets=[
                Widget(
                    'label',
                    converter=DojoComboValueConverter('label'),
                    filter=StringFilter(otherField, operation="contains"))
            ]
        )
    )


class PeriodicRefreshWidget(BooleanWidget):
    period = 5000
    placeholder = _("Refresh every %i sec") % (period / 1000)
    templateName = "periodic_refresh"
    filterClass = NoFilter

    def exportDescription(self, requestDict):
        return


class PeriodicOlderThanNowRefreshWidget(PeriodicRefreshWidget):
    filterClass = OlderThanNow
