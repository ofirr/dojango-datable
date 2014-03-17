from datetime import date
from datetime import datetime


class NoFilter:
    def __init__(self, field, operation=None):
        pass

    def filterQuerySet(self, querySet, value):
        return querySet

class SimpleFilter:
    """This is an object, which is able to filter a QuerySet
    using an operation. It also performs a 'cleaning' operation
    on the input value (the filter parameter).
    """

    operation = "eq"

    def __init__(self, field, operation=None):
        self.field = field

        if operation is not None:
            self.operation = operation

    def clean(self, value):
        """By default, we just return this value"""
        return value

    def filterQuerySet(self, querySet, value):
        """This modifies a QuerySet by filtering it, or just returns
        it in case there are no modifications. The value has not
        been cleaned yet!"""

        if value is None:
            return querySet

        safe_value = self.clean(value)

        if safe_value is None:
            return querySet

        return self.enabled(querySet, safe_value)

    def enabled(self, querySet, safe_value):
        """The filter is enabled -- we don't check anything at this point,
        we just want to do the filtering right now. Value has been checked
        to be safe & properly fomatted so we can just blindly filter
        the query set here.
        """

        fn = self.field
        if self.operation != "eq":
            fn = self.field + "__" + self.operation

        kw = {fn: safe_value}
        return querySet.filter(**kw)


class TypedFilter(SimpleFilter):
    allowedTypes = None

    def __init__(self, field, allowedTypes=None, *args, **kw):
        SimpleFilter.__init__(self, field, *args, **kw)

        if allowedTypes is not None:
            self.allowedTypes = allowedTypes

    def clean(self, value):
        if type(value) not in self.allowedTypes:
            err = "Type %r not supported by this filter" % type(value)
            raise TypeError(err)

        return value


class IntegerFilter(TypedFilter):
    allowedTypes = [int]

class StringFilter(TypedFilter):
    allowedTypes = [unicode, str]


class DateTimeFilter(TypedFilter):
    allowedTypes = [datetime, date]


class DateFilter(TypedFilter):
    allowedTypes = [date]


class BooleanFilter(TypedFilter):
    allowedTypes = [bool]
