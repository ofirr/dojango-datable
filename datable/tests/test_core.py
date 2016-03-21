from ludibrio import Mock

from django.test import TestCase
from django.utils.translation import ugettext as _

from datetime import datetime, date, timedelta
import pytz

from datable import core
from datable.core import formats

class TestSimpleFilter(TestCase):
    def test_simple(self):
        f = core.SimpleFilter('field')
        self.assertEquals(f.operation, 'eq')

        f = core.SimpleFilter('field', 'operation')
        self.assertEquals(f.operation, 'operation')

    def test_filterQuerySet_clean(self):
        f = core.SimpleFilter('foo')

        f.clean = lambda x: 5

        with Mock() as querySet:
            querySet.filter(foo=5)

        f.filterQuerySet(querySet, 'not 5')

        querySet.validate()

    def test_enabled(self):
        f = core.SimpleFilter('foo', 'contains')
        with Mock() as querySet:
            querySet.filter(foo__contains='bar')

        f.enabled(querySet, 'bar')
        querySet.validate()

class TestTypedFilter(TestCase):
    def test_typed(self):
        f = core.TypedFilter('foo', allowedTypes=[str, str])
        self.assertEquals('foo', f.clean('foo'))
        self.assertEquals('foo', f.clean('foo'))
        self.assertRaises(TypeError, f.clean, 5)

# ##########################################################

class TestJSValueConverter(TestCase):
    def test_converter(self):
        j = core.JSValueConverter('foo')
        self.assertRaises(NotImplementedError, j.valueFromJS, {'foo':5})
        self.assertRaises(NotImplementedError, j.valueToJS, 5)

    def test_existsIn(self):
        j = core.JSValueConverter('foo')
        requestDict = {'foo':5}
        self.assertEquals(j.existsIn(requestDict), True)
        requestDict = {'bar':5}
        self.assertEquals(j.existsIn(requestDict), False)

class TestStringValueConverter(TestCase):
    def test_stringConverter(self):
        j = core.StringValueConverter('foo')

        self.assertEquals(j.valueFromJS({'foo':5}), 5)

        self.assertEquals(j.valueToJS(5), str('5'))
        self.assertEquals(j.valueToJS(None), None)


class TestDateTimeValueConverter(TestCase):
    def test_datetimeValueConverter(self):
        j = core.DateTimeValueConverter('foo')

        x = datetime.now(pytz.utc)
        self.assertEquals(j.convertToJS(x), x.isoformat())
        self.assertEquals(j.convertFromJS(x.isoformat()), x)


class TestDateValueConverter(TestCase):
    def test_DateValueConverter(self):
        j = core.DateValueConverter('foo')

        x = date(2011, 11, 11)
        self.assertEquals(j.convertToJS(x), '2011-11-11')
        self.assertEquals(j.convertFromJS('2011-11-11'), x)

class TestBooleanConverter(TestCase):
    def test_booleanConverter(self):
        j = core.BooleanConverter('foo')

        self.assertEquals(j.convertToJS(True), 'true')
        self.assertEquals(j.convertToJS(False), 'false')
        self.assertEquals(j.convertToJS(1), 'true')
        self.assertEquals(j.convertToJS(0), 'false')
        self.assertEquals(j.convertToJS(None), 'null')

        self.assertEquals(j.convertFromJS('true'), True)
        self.assertEquals(j.convertFromJS('asdf'), False)


class TestIntegerConverter(TestCase):
    def test_integerConverter(self):
        j = core.converters.IntegerConverter('z')
        self.assertEquals(j.convertToJS(15), '15')
        self.assertEquals(j.convertFromJS('15'), 15)
        self.assertEquals(j.convertFromJS('XX'), None)
        self.assertEquals(j.convertFromJS(None), None)

        j = core.converters.IntegerConverter('z', min=6)
        self.assertEquals(j.convertFromJS('5'), None)
        self.assertEquals(j.convertFromJS('15'), 15)


class TestIntegerConverter(TestCase):
    def test_dojoComboValueConverter(self):
        j = core.converters.DojoComboValueConverter('z')
        self.assertEquals(j.convertFromJS('wtf*'), 'wtf')
        self.assertEquals(j.convertFromJS('XX'), 'XX')
        self.assertEquals(j.convertFromJS(''), None)

# ##########################################################

class TestFieldSerializer(TestCase):
    def test_fieldSerializer(self):
        f = core.serializers.FieldSerializer('foo')
        with Mock() as mock:
            mock.__getattr__('foo') >> True
            mock.__getattr__('foo') >> True

        self.assertEquals(
            f.extract_value(mock), True)

        self.assertRaises(
            NotImplementedError,
            f.serialize, mock)

        self.assertRaises(
            NotImplementedError,
            f.serialize_value, 'foo')

    def test_modelSerializer(self):
        class Foo:
            def __unicode__(self):
                return 'bar'

        s = core.serializers.UnicodeSerializer()
        self.assertEquals(s.serialize(Foo()), 'bar')

    def test_formatSerializer(self):
        class Foo:
            bar = '1'
            baz = 'quux'

        s = core.serializers.FormatStringSerializer("%(bar)s %(baz)s")
        self.assertEquals(s.serialize(Foo()), "1 quux")


class TestSerializerMixin:
    firstValue = None
    shouldBe = []
    klass = None

    def setUp(self):
        with Mock() as mock:
            mock.__getattr__('foo') >> self.firstValue
            mock.__getattr__('foo') >> None
        self.mock = mock

    def test_serializer(self):
        f = self.klass('foo')
        self.assertEquals(f.serialize(self.mock), self.shouldBe[0])
        self.assertEquals(f.serialize(self.mock), self.shouldBe[1])
        self.mock.validate()


class TestStringSerializer(TestSerializerMixin, TestCase):
    firstValue = '123'
    klass = core.StringSerializer
    shouldBe = ['123', _('[no data]')]


class TestBooleanSerializer(TestSerializerMixin, TestCase):
    firstValue = True
    klass = core.BooleanSerializer
    shouldBe = [_('yes'), _('[no data]')]


class TestDateSerializer(TestSerializerMixin, TestCase):
    firstValue = date(2011, 11, 11)
    klass = core.DateSerializer
    shouldBe = ['2011-11-11', _('[no data]')]


class TestDateTimeSerializer(TestSerializerMixin, TestCase):
    firstValue = datetime(2011, 11, 11, 11, 11, 11)
    klass = core.DateTimeSerializer
    shouldBe = ['2011-11-11 11:11:11', _('[no data]')]


class TestTimedeltaSerializer(TestSerializerMixin, TestCase):
    firstValue = timedelta(seconds=5)
    klass = core.TimedeltaSerializer
    shouldBe = [_('%i.00 sec.') % 5, _('[no data]')]


class TestForeignKeySerializer(TestCase):
    def test_foreignKeySerializer(self):
        u = core.ForeignKeySerializer(
            'foo',
            other_serializer=core.StringSerializer('name')
            )

        with Mock() as fakeobj2:
            fakeobj2.__getattr__('name') >> 'bar'

        with Mock() as fakeobj:
            fakeobj.__getattr__('foo') >> fakeobj2

        self.assertEquals(u.serialize(fakeobj), 'bar')

    def test_getName(self):
        u = core.ForeignKeySerializer(
            'foo',
            core.ForeignKeySerializer(
                'bar',
                core.StringSerializer('baz')
                )
            )

        self.assertEquals('foo__bar__baz', u.getFieldName())


class TestURLSerializer(TestCase):
    def test_urlSerializer(self):
        u = core.URLSerializer(field='foo', urlName='bar')

        with Mock() as resolver:
            resolver('bar', args=(1, )) >> True
        u.resolver = resolver

        self.assertEquals(u.serialize_value(None), None)
        self.assertEquals(u.serialize_value(1), True)


class TestHrefSerializer(TestCase):

    def test_hrefSerializer(self):
        u = core.HrefSerializer(
            format='%(foo)s',
            urlSerializer=core.URLSerializer(
                field='bar',
                urlName='quuz')
            )

        with Mock() as model:
            model.__getattr__('foo') >> 'baz'

            model.__getattr__('foo') >> 'baz'
            model.__getattr__('bar') >> 'quux'

        with Mock() as resolver:
            resolver('quuz', args=('quux', )) >> 'http://lol/'
        u.urlSerializer.resolver = resolver

        ret = u.serialize(model, output_format=formats.XLS)
        self.assertEquals(ret, 'baz')

        ret = u.serialize(model, output_format=formats.JSON)
        self.assertEquals(ret, 'http://lol/\nbaz')




def fakeQuerySet():
    with Mock() as mock:
         for a in [1,2,3]:
             mock.__getattr__('foo') >> 123
             mock.__getattr__('pk') >> a

    return [mock, mock, mock]


def fakeQuerySetNoIDs():
    with Mock() as mock:
         for a in [1,2,3]:
             mock.__getattr__('foo') >> 123

    return [mock, mock, mock]


from datable.core.serializers import StringSerializer

class FakeColumn:
    getName = lambda self: 'foo'
    getSerializer = lambda self: StringSerializer('foo')


class TestQuerySetSerializer(TestCase):
    def test_querySetSerializer(self):
        f = core.QuerySetSerializer([
            FakeColumn()
        ])

        l = list(f.serialize(fakeQuerySetNoIDs()[:1]))
        self.assertEquals(l, [{'foo':'123'}])


class TestFormats(TestCase):
    def test_getExtension(self):
        self.assertEquals(
            'xls', core.formats.getExtension(core.formats.XLS))
