from datetime import date, datetime

from ludibrio import Mock

from django.test import TestCase

from datable.web import widgets


class TestWidget(TestCase):
    def test_baseWidget_init(self):
        self.assertRaises(
            Exception,
            widgets.Widget, {})

    def test_baseWidget(self):
        f = widgets.StringWidget('name')
        self.assertEquals(f.name, 'name')

    def test_baseWidget_2(self):
        f = widgets.StringWidget('name')
        self.assertEquals(f.initialValue, None)

        d = {'foo': 'bar'}
        self.assertNotEquals(f.existsIn(d), True)

        d = {'name': 'lol'}
        self.assertEquals(f.existsIn(d), True)

    def test_baseWidget_typeCheck(self):
        kw = dict(name='123', jsName='123', initialValue='string!')
        self.assertRaises(TypeError, widgets.Widget, **kw)

    def test_widget_valueToJS(self):
        f = widgets.StringWidget('jsName')
        self.assertEquals('123', f.converter.valueToJS('123'))

    def test_baseWidget_exportDescription(self):
        f = widgets.StringWidget('name')
        self.assertEquals(
            f.exportDescription(dict(name='123')), ['Name', '123'])


class TestStringWidget(TestCase):
    def test_stringWidget_filterQuerySet_when_requestDict_value_is_None(self):
        flt = widgets.StringWidget('foo')
        querySet = [1, 2, 3]
        requestDict = {'foo': None}

        self.assertEquals(
            flt.filterQuerySet(querySet, requestDict),
            querySet)

    def test_stringWidget_filterQuerySet(self):
        w = widgets.StringWidget('foo')
        requestDict = {'foo': 'omg'}
        with Mock() as querySet:
            querySet.filter(foo__contains='omg')

        w.filterQuerySet(querySet, requestDict)


class TestDateWidget(TestCase):
    def test_dateWidget(self):
        flt = widgets.DateWidget('foo')
        requestDict = {'foo': '2011-01-11'}
        with Mock() as querySet:
            querySet.filter(foo=date(2011, 1, 11))

        flt.filterQuerySet(querySet, requestDict)

    def test_dateWidget_lte(self):
        flt = widgets.DateWidget('foo', filterKwargs={'operation': 'lte'})
        requestDict = {'foo': '2011-01-11'}
        with Mock() as querySet:
            querySet.filter(foo__lte=date(2011, 1, 11))
        flt.filterQuerySet(querySet, requestDict)

    def test_dateWidget_initial(self):
        kw = dict(name="name", initialValue=datetime(2011, 1, 1))
        widgets.DateWidget(**kw)

        kw = dict(name="name", initialValue=date(2011, 1, 1))
        widgets.DateWidget(**kw)
