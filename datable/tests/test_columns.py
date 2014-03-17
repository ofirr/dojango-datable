from datetime import timedelta, datetime

from django.test import TestCase
from django.utils.translation import ugettext as _

from datable.web.columns import Column


class MockRow:
    pass


class TestColumn(TestCase):
    def test_serializer(self):

        c = Column('mock')

        for data, result in [
            (None, _('[no data]')),
            (timedelta(days=50), _('%.2f sec.') % 4320000),
            (datetime(2011, 11, 11, 11, 11, 11),
             '2011-11-11 11:11:11'),
            (123, '123'),
            (123.123, '123.123'),
            ('foo', 'foo'),
            (u'foo', 'foo')
            ]:
            m = MockRow()
            m.mock = data
            returned = c.serialize(m)
            self.assertEquals(returned, result)
