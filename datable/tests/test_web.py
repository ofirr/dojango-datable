from django.http import Http404

from datable.web import columns
from datable.web import widgets
from datable.core import converters
from datable.web import storage
from datable.core.serializers import StringSerializer
from datable.core.serializers import PrimaryKeySerializer
from datable.web import serializers
from datable.web import table
from datable.web.util import getFullPath

import json

from ludibrio import Mock, Stub
from django.test import TestCase
from datable.tests.test_core import fakeQuerySet
from datable.tests.test_core import FakeColumn
from datable.tests.test_core import fakeQuerySetNoIDs
from datetime import datetime
from datable.core import formats
from cStringIO import StringIO

# # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # #

class TestColumn(TestCase):
    def test_raises_noSerializerClass(self):
        self.assertRaises(Exception, columns.Column)

class TestStringColumn(TestCase):
    def test_stringColumn(self):
        s = columns.StringColumn('foo')

        with Mock() as querySet:
            querySet.order_by('foo')
            querySet.order_by('-foo')

        s.sortQuerySet(querySet, False)
        s.sortQuerySet(querySet, True)

    def test_getName(self):
        s = columns.StringColumn('foo')
        self.assertEquals(s.getName(), 'foo')

    def test_getSerializer(self):
        s = columns.StringColumn('foo')
        self.assertEquals(s.getSerializer(), s.serializer)

    def test_getLabel(self):
        s = columns.StringColumn('foo')
        self.assertEquals(s.getLabel(), s.label)

    def test_sortQuerySet(self):

        with Mock() as querySet:
            querySet.order_by('foo')
            querySet.order_by('bar')

        s = columns.StringColumn('foo')
        s.sortQuerySet(querySet, False)

        s = columns.StringColumn(
            'foo', sortColumnName='bar')

        s.sortQuerySet(querySet, False)
        querySet.validate()


# # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # #

class TestWidgets(TestCase):
    def test_raises(self):
        self.assertRaises(
            Exception, widgets.Widget, 'foo')

    def test_getName(self):
        w = widgets.StringWidget('foo')
        self.assertEquals(w.getName(), 'foo')

    def setUp(self):
        self.w = widgets.StringWidget('foo')

    def test_widgets(self):
        self.assertEquals(self.w.initialValue_js, None) # 'null')

    def test_request_good(self):
        requestDict = {'foo': '5'}

        self.assertEquals(self.w.existsIn(requestDict), True)

        self.assertEquals(
            self.w.exportDescription(requestDict),
            ['Foo', '5'])

        with Mock() as querySet:
            querySet.filter(foo='5')

        self.w.filterQuerySet(querySet, requestDict)

        querySet.validate()


    def test_request_good(self):
        requestDict = {'bar': '5'}
        self.assertEquals(self.w.existsIn(requestDict), False)


# # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # ## # # #


class TestJSONQuerySetSerializer(TestCase):

    def test_jsonQuerySetSerializer(self):
        f = serializers.JSONQuerySetSerializer([
            FakeColumn()
        ])

        res = f.serialize(fakeQuerySet(), 3)
        self.assertEquals(res['numRows'], 3)


class TestXLSQuerySetSerializer(TestCase):
    def test_xlsQuerySetSerializer(self):
        x = serializers.XLSQuerySetSerializer([
            FakeColumn()
        ])

        xls_file = x.serialize(fakeQuerySetNoIDs(),
                               'tytul', ['nag', 'lowek'],
                               [['exp'], ['exp']])


class TestCSVQuerySetSerializer(TestCase):

    def test_csvQuerySetSerializer(self):

        x = serializers.CSVQuerySetSerializer([
            FakeColumn()
        ])

        csv_file = x.serialize(fakeQuerySetNoIDs(),
                               'tytul', ['nag', 'lowek'],
                               [['exp'], ['exp']])


## # #  # # # #  # # #

class FakeRequest:
    secure = True
    is_secure = lambda self: self.secure
    META = {'HTTP_HOST': 'test.host'}
    path = '/lol'

class TestWebUtil(TestCase):
    def test_getFullPath(self):

        fr = FakeRequest()

        self.assertEquals(
            'https://test.host/lol',
            getFullPath(fr))

        fr.secure = False

        self.assertEquals(
            'http://test.host/lol',
            getFullPath(fr))

## # # # # # (@*#(* $(#* #)($ )#($ )#( )$( )( #)($ )#( )(# $

class TestStorage(TestCase):
    def setUp(self):
        self.w = widgets.StringWidget('foo', filterKwargs=dict(operation="contains"))
        self.c = columns.StringColumn('foo')

        self.s = storage.Storage(
            None,
            widgets=[self.w],
            columns=[self.c]
            )

        self.valueDict = {'table': None, 'foo': '5', 'sort': '-foo'}

    def test_defaultSort(self):
        s = storage.Storage(
            None, columns=[self.c],
            defaultSort='-foo')
        self.assertEquals(s.defaultSort, (self.c, True))
        s = storage.Storage(
            None, columns=[self.c],
            defaultSort='foo')
        self.assertEquals(s.defaultSort, (self.c, False))

    def test_filterAndSort(self):
        with Mock() as querySet:
            querySet.filter(foo__contains='5')
            querySet.order_by('-foo')

        self.s.querySet = querySet
        self.s.filterAndSort(self.valueDict, (self.c, True))
        querySet.validate()

    def test_defaultSort(self):
        with Mock() as querySet:
            querySet.filter(foo__contains='5')
            querySet.order_by('-foo')

        self.s.defaultSort = (self.c, True)
        self.s.querySet = querySet
        self.s.filterAndSort(self.valueDict, None)
        querySet.validate()


    def test_getWidgets(self):
        self.assertEquals(
            self.s.getWidgets(),
            [self.w])

    def test_getWidget(self):
        self.assertEquals(
            self.s.getWidget('foo'),
            self.w)

    def test_getColumns(self):
        self.assertEquals(
            self.s.getColumns(),
            [self.c]
        )

    def test_getColumnName(self):
        self.assertEquals(self.c, self.s.getColumn('foo'))

    def test_getColumnIndex(self):
        self.assertEquals(0, self.s.getColumnIndex('foo'))

    def test_getSerializers(self):
        self.assertEquals(
            self.s.getSerializers(),
            [self.c.getSerializer()])

    def test_getHeader(self):
        self.assertEquals(
            self.s.getHeader(),
            ['Foo'])

    def test_describeExportData(self):
        res = list(self.s.describeExportData(self.valueDict))
        self.assertEquals(res[-1][0], 'Foo')

    def test_serializeToJSON(self):

        class Foo:
            pk = 1
            foo = 'bar'

        with Mock() as querySet:
            querySet.filter(foo__contains='5')
            querySet.order_by('-foo')
            querySet.count() >> 1
            querySet.__getitem__(slice(0, None, None)) >> [Foo()]

        self.s.querySet = querySet

        res = self.s.serializeToJSON(self.valueDict, (self.c, True))
        self.assertIn("'pk': 1", str(res))

        querySet.validate()

    def test_serializeToCSV(self):

        class Foo:
            foo = 'bar'

        with Mock() as querySet:
            querySet.filter(foo__contains='5')
            querySet.order_by('-foo')
            querySet.__getitem__(0) >> Foo()
            querySet.__getitem__(1) >> StopIteration()

        self.s.querySet = querySet
        res = self.s.serializeToCSV(self.valueDict, (self.c, True))
        querySet.validate()

    def test_serializeToXLS(self):

        class Foo:
            foo = 'bar'

        with Mock() as querySet:
            querySet.filter(foo__contains='5')
            querySet.order_by('-foo')
            querySet.__getitem__(0) >> Foo()
            querySet.__getitem__(1) >> StopIteration()

        self.s.querySet = querySet
        res = self.s.serializeToXLS(self.valueDict, (self.c, True))
        querySet.validate()



# ###*  ##*# # # **# ** #* # **#* #**# #* *# *# *# * #**# *#* *#* #*

class TestTable(TestCase):

    skip = 'foo'

    def setUp(self):
        self.c = columns.StringColumn('foo')
        self.w = widgets.StringWidget(
            'foo', filterKwargs=dict(operation="contains"))

        self.s = storage.Storage(
            None,
            widgets=[self.w],
            columns=[self.c]
            )

        self.t = table.Table(
            name='table',
            storage=self.s)

        self.requestDict = {'table':None,'foo':'5', 'sort':'-foo'}

        class FakeRequest:
            META = {'HTTP_HOST': 'localhost'}
            is_secure = lambda x=None: False
            path = '/lol'
            GET = self.requestDict

        self.fakeRequest = FakeRequest()

    def test_getSortColumn(self):

        col, desc = self.t.getSortColumn({'sort':'foo'})
        self.assertEquals(col, self.c)
        self.assertEquals(desc, False)

        col, desc = self.t.getSortColumn({'sort':'-foo'})
        self.assertEquals(col, self.c)
        self.assertEquals(desc, True)

        res = self.t.getSortColumn({'sort':'lol'})
        self.assertEquals(res, None)

        res = self.t.getSortColumn({})
        self.assertEquals(res, None)

    def test_filterAndSort(self):
        with Mock() as storage:
            storage.getColumns() >> []
            storage.filterAndSort(self.requestDict, None)

        self.t.storage = storage
        self.t.filterAndSort(self.fakeRequest)
        storage.validate()

    def test_getExportFilename(self):
        self.t.filename = 'test-%Y'
        y = datetime.now().strftime('%Y')
        self.assertEquals(
            self.t.getExportFilename(formats.CSV),
            'filename=test-%s.csv' % y)

    def test_fileResponse(self):
        res = self.t.fileResponse(StringIO("test"), formats.XLS)
        self.assertIn('Content-Length: 4', str(res))
        self.assertIn('test', str(res))

    def test_willHandle(self):
        self.assertEquals(
            self.t.willHandle(self.fakeRequest),
            True)

    def test_handleRequest(self):
        f = self.fakeRequest

        self.t.storage = Stub()
        self.t.fileResponse = Stub()
        self.t.jsonResponse= Stub()

        for value in ['xls', 'json', 'csv']:
            f.GET = dict(table=value)
            self.t.handleRequest(f)

    def test_handleRequest_filter(self):
        f = self.fakeRequest

        f.GET['table']="filter,xxx"
        self.assertRaises(
            Http404, self.t.handleRequest, f)

        with Mock() as other_storage:
            other_storage.__len__() >> True
            other_storage.serializeToJSON(dict(
                foo='5'
            ), None) >> {'a':'b'}

        self.w.storage = other_storage
        f.GET['table']="widget,foo"
        resp = self.t.handleRequest(f, 'GET')

        self.assertEquals(str(resp).split('\n')[-1], '{"a": "b", "success": true}')

    def test_getStorage(self):
        self.assertEquals(self.s, self.t.getStorage())

