from datetime import date
from datetime import datetime

from django.test import TestCase

from datable.web.extra import widgets as extra_widgets
from datable.web.extra import filters as extra_filters

from ludibrio import Mock
from ludibrio import Stub

class TestExtraWidgets(TestCase):
    def test_widgets(self):
        from datable.web.extra.widgets import DateLessOrEqual

    def test_foreginKeyComboBox(self):
        f = extra_widgets.ForeignKeyComboBox(
            'foo', None, None
        )


class TestExtraFilters(TestCase):
    def test_olderThanNow(self):
        f = extra_filters.OlderThanNow('foo')
        s = Stub()
        f.enabled(s, True)

    def test_biggerThan(self):
        f = extra_filters.BiggerThan('foo', 5)

        with Mock() as querySet:
            querySet.filter(foo__gt=5)
        f.enabled(querySet, True)

    def test_wholeDayFilter(self):
        f = extra_filters.WholeDayFilter('foo')

        with Mock() as querySet:
            querySet.filter(
                foo__gte=date(2011, 12, 31),
                foo__lt=date(2012, 1, 1))

            querySet.filter(
                foo__gte=date(2011, 12, 31),
                foo__lt=date(2012, 1, 1))

        f.filterQuerySet(querySet, date(2011, 12, 31))
        f.filterQuerySet(querySet, datetime(2011, 12, 31, 12, 32))
