from datable.core.filters import BooleanFilter
from datable.core.filters import DateFilter

from datetime import datetime
from datetime import date
from datetime import timedelta


class OlderThanNow(BooleanFilter):
    def enabled(self, querySet, safe_value):
        if safe_value == True:
            kw = {self.field + "__lte": datetime.now()}
            return querySet.filter(**kw)
        return querySet


class BiggerThan(BooleanFilter):
    def __init__(self, field, value):
        BooleanFilter.__init__(self, field, operation="gt")
        self.value = value

    def enabled(self, querySet, safe_value):
        if safe_value == True:
            kw = {self.field + "__gt": self.value}
            return querySet.filter(**kw)
        return querySet


class WholeDayFilter(DateFilter):
    """When given a date (or datetime), use this value to find
    records with the same day value - since day 00:00:00, until next day 00:00
    """

    allowedTypes = [datetime, date]

    def clean(self, value):
        value = DateFilter.clean(self, value)
        if type(value) == datetime:
            return value.date()
        return value

    def enabled(self, querySet, safe_value):
        this_day = safe_value
        next_day = this_day + timedelta(days=1)

        return querySet.filter(
            **{self.field + "__gte": this_day,
              self.field + "__lt": next_day}
            )
