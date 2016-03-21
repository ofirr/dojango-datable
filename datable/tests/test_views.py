# -*- encoding: utf-8 -*-

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.translation import ugettext as _
from django.http import Http404

from ludibrio import Mock

from datable.core import filters
from datable.core import formats
from datable.web import columns
from datable.web.util import getFullPath
from datable.web.table import Table
from datable.web.storage import Storage
from datable.web import widgets

users_datable = Table(
    name='users',
    storage=Storage(
        querySet=User.objects.all(),
        columns=[('username', 'Login'),
            ('first_name', 'First name'),
            ('last_name', 'Last name'),
            ('foo', 'FOO', lambda x: 'foo')]
        ))

class FakeRequest:
    secure = True
    is_secure = lambda self: self.secure
    META = {'HTTP_HOST': 'test.host'}
    path = '/lol'

class TestViews(TestCase):
    def test_getFullPath(self):

        fr = FakeRequest()

        self.assertEquals(
            'https://test.host/lol',
            getFullPath(fr))

        fr.secure = False

        self.assertEquals(
            'http://test.host/lol',
            getFullPath(fr))

class TestTable(TestCase):

    def test_badInit(self):
        kw = dict(name="", querySet=None, columns=[])
        self.assertRaises(ValueError, Table, **kw)

        kw['name'] = None
        self.assertRaises(ValueError, Table, **kw)

        kw['name'] = 'sort'
        self.assertRaises(ValueError, Table, **kw)

        kw['name'] = 'lol'
        Table(**kw)

    def test_defaultSort_good(self):
        kw = dict(name="fa", querySet=None, columns=[
            columns.Column('foo')],
            initialSort='foo')
        d = Table(**kw)
        self.assertEquals(d.initialSort, 1)

        kw['initialSort'] = '-foo'
        d = Table(**kw)
        self.assertEquals(d.initialSort, -1)

    def test_defaultSort_bad(self):
        kw = dict(name="fa", querySet=None, columns=[
            columns.Column('foo')],
            initialSort='unexistent')
        d = Table(**kw)
        self.assertEquals(d.initialSort, None)

    def test_serialize(self):
        User.objects.all().delete()
        User.objects.create_user('datable-test-user', 'foo@bar.pl')

        self.assertEquals(
            users_datable.header(),
            ['Login', 'First name', 'Last name', 'FOO'])

        for element in users_datable.serialize(
            User.objects.all().order_by('username')[:2]
            ):
            k = list(element.keys())
            self.assertEquals(
                k,
                ['username', 'first_name', 'last_name', 'foo'])
            self.assertEquals(element['username'], 'datable-test-user')
            self.assertEquals(element['foo'], 'foo')
            break

    def test_badInit_duplicateFilterNameError(self):
        kw = dict(name='name',
                  querySet='querySet',
                  columns=[],
                  filters=[
                    filters.StringFilter('foo'),
                    filters.StringFilter('foo')
                    ])
        self.assertRaises(
            filters.DuplicateFilterNameError, Table, **kw)

    def test_badInit_filterNameError(self):
        kw = dict(name='name',
                  querySet=None,
                  columns=[],
                  filters=[
                    filters.StringFilter('name')
                  ])
        self.assertRaises(
            filters.FilterNameError, Table, **kw)


    def test_performFilteringAndSorting(self):
        class FakeRequest:
            GET = dict(sort='first_name', start=0, count=2)
        d = Table("name", User.objects.all(), [('first_name', 'label')])
        d.performFilteringAndSorting(FakeRequest())


    def test_wrong_sort_column(self):
        class FakeRequest:
            GET = dict(sort='first_name', start=0, count=2)
        # No column 'first name' in the set:
        d = Table("name", User.objects.all(), [('column', 'label')])
        self.assertRaises(
            columns.ColumnNotFound,
            d.performFilteringAndSorting, FakeRequest())

    def test_serializeRow(self):
        class FakeModel:
            foo = '123'

        fm = FakeModel()

        with Mock() as column:
            column.name >> "foo"
            column.serialize(fm, output=0) >> 'bar'

        d = Table("name", 'querySet', [column])
        self.assertEquals(
            d.serializeRow(fm, output=0),
            {'foo':'bar'})

    def test_serializeData(self):
        class FakeModel:
            foo = '1'

        queryset = [FakeModel(), FakeModel()]

        d = Table("name", 'querySet', [('foo', 'label')])

        with Mock() as d.serializeRow:
            d.serializeRow(1, None)
            d.serializeRow(1, None)

        d.serializeData(queryset, output=None)

    def test_getExportFileName(self):
        d = Table('name', 'querySet', [])
        self.assertEquals(
            "filename=name.xls", d.getExportFileName(output=formats.XLS))

        self.assertEquals(
            "filename=mine.xls", d.getExportFileName(output=formats.XLS,
                                            name="mine"))

        self.assertEquals(
            "filename=%C5%82%C3%B3d%C5%BA_jest.xls",
            d.getExportFileName(output=formats.XLS, name="łódź jest"))

    def test_serializeToJSON(self):
        class FakeRequest:
            GET = dict(sort='first_name', start=0, count=2)
        d = Table("name", User.objects.all(), [('first_name', 'label')])
        d.serializeToJSON(FakeRequest())

    def test_serialize(self):

        class F:
            no_calls = 0

        def call(*args, **kw):
            F.no_calls += 1

        d = Table("name", "querySet", [])
        d.serializeToJSON = call
        d.serializeToCSV = call
        d.serializeToXLS = call

        for fmt in [formats.XLS, formats.JSON, formats.CSV]:
            d.serialize(None, fmt)

        self.assertEquals(F.no_calls, 3)

        self.assertRaises(
            formats.UnknownFormat,
            d.serialize, None, 'unknown format')

    def test_header(self):
        d = Table("name", "querySet", [('lol', 'omg')])
        self.assertEquals(d.header(), ['omg'])

    # Export tests => TestTableExports

    def test_willHandle(self):
        f = FakeRequest()
        f.GET = {'datable': 'json'}
        f.POST = {}
        d = Table('datable', None, [])

        self.assertEquals(d.willHandle(f), True)

        self.assertNotEquals(d.willHandle(f, method='POST'), True)

        f.GET = {'no':'such table'}
        self.assertNotEquals(d.willHandle(f), True)

class TestTableGetSortColumn(TestCase):
    def setUp(self):

        class FakeRequest:
            GET = dict(sort='first_name', start=0, count=2)

        self.fakeRequest = FakeRequest()
        self.column = columns.StringColumn('first_name', 'label')
        self.d = Table("name", storage=Storage(
            querySet=User.objects.all(),
            columns=[self.column]))

    def test_getSortColumn_asc(self):
        self.assertEquals(
            (self.column, False),
            self.d.getSortColumn(self.fakeRequest.GET)
            )

    def test_getSortColumn_desc(self):
        self.fakeRequest.GET['sort'] = '-first_name'
        self.assertEquals(
            (self.column, True),
            self.d.getSortColumn(self.fakeRequest.GET)
            )

    def test_getSortColumn_err(self):
        self.fakeRequest.GET['sort'] = 'unEXistEnt'
        self.assertEquals(self.d.getSortColumn(self.fakeRequest.GET), None)


class TestTableHandleRequest(TestCase):
    def call(self, *args, **kw):
        self.no_calls += 1

    def setUp(self):
        self.no_calls = 0

        self.req = FakeRequest()

        self.req.GET = {'start':0, 'count':25}
        self.req.POST = {}

        User.objects.create_user('username', 'email-username')
        User.objects.create_user('username2', 'email-username2')
        User.objects.create_user('username3', 'email')

        self.d = Table(
            'datable',
            storage=Storage(
                querySet=User.objects.all(),
                columns=[columns.StringColumn('email', 'E-mail')],
                widgets=[widgets.StringWidget(name='exists')]
                )
            )


    def test_handleRequest(self):

        for fmt in ['xls', 'csv', 'json']:
            self.req.GET['datable'] = fmt
            res = self.d.handleRequest(self.req)
            self.assertIn('username2', res.content)

        self.req.GET = {'datable': 'filter,exists' }
        self.assertRaises(
            Http404,
            self.d.handleRequest, self.req)


    def test_handleRequest_badFormat(self):
        self.req.GET = {'datable': 'unknown format'}
        self.assertRaises(Http404, self.d.handleRequest, self.req)

    def test_handleRequest_noSuchFilter(self):
        self.req.GET = {'datable': 'filter,does not exist'}
        self.assertRaises(Http404, self.d.handleRequest, self.req)


class TestTableExports(TestCase):

    def setUp(self):
        for a in range(5):
            User.objects.create_user('datable-test-user%i' % a, 'foo@bar.pl')

        self.d = Table(
            "name",
            storage=Storage(
                querySet=User.objects.all(),
                columns=[columns.StringColumn('email', 'E-mail')],
                widgets=[widgets.StringWidget('email', label="E-mail", initialValue='foo')])
            )

        self.request = FakeRequest()
        self.request.GET = {'email':'foo@'}

    def test_exportDescription(self):
        res = list(self.d.storage.describeExportData(self.request.GET))
        self.assertEquals(res[0][0], _('Exported on'))
        self.assertEquals(res[1][0], _('E-mail'))
        self.assertIn(['E-mail', 'foo@'], res)

    def test_serializeToCSV(self):
        res = self.d.storage.serializeToCSV(self.request.GET, None)

    def test_serializeToXLS(self):
        res = self.d.storage.serializeToXLS(self.request.GET, None)
