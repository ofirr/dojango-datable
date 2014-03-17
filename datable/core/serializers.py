# Field serializers serialize fields of model

from django.core.urlresolvers import reverse

from django.utils.translation import ugettext as _
from django.utils.datastructures import SortedDict

from datable.core import formats

class UnicodeSerializer:
    def serialize(self, model, output_format=None):
        return unicode(model)


class DictProxy:
    def __init__(self, original):
        self.original = original

    def __getitem__(self, name):
        return getattr(self.original, name

                       )
class FormatStringSerializer:

    def __init__(self, format):
        self.format = format

    def asDict(self, model):
        return DictProxy(model)

    def serialize(self, model, output_format=None):
        return self.format % self.asDict(model)


class FieldSerializer:
    """I serialize single field of a single item to a specific
    format."""

    getterFunction = getattr

    def __init__(self, field, getterFunction=None):
        self.field = field
        if getterFunction is not None:
            self.getterFunction = getterFunction

    def getFieldName(self):
        return self.field

    def extract_value(self, model):
        return self.getterFunction(model, self.field)

    def serialize_value(self, value, output_format=None):
        raise NotImplementedError

    def serialize(self, model, output_format=None):
        return self.serialize_value(
            self.extract_value(model), output_format)

    def getFieldName(self):
        return self.field


class StringSerializer(FieldSerializer):

    def serialize_value(self, value, output_format=None):
        if value is None:
            return _('[no data]')

        return unicode(value)


class PrimaryKeySerializer(StringSerializer):
    def __init__(self):
        StringSerializer.__init__(self, field='pk')


class DateTimeSerializer(FieldSerializer):
    def serialize_value(self, value, output_format=None):
        if value is None:
            return _('[no data]')

        return value.strftime("%Y-%m-%d %H:%M:%S")


class DateSerializer(FieldSerializer):
    def serialize_value(self, value, output_format=None):
        if value is None:
            return _('[no data]')

        return value.strftime("%Y-%m-%d")


class BooleanSerializer(FieldSerializer):
    def serialize_value(self, value, output_format=None):
        if value is None:
            return _('[no data]')

        if value:
            return _('yes')

        return '-'


class TimedeltaSerializer(FieldSerializer):
    def serialize_value(self, value, output_format=None):
        if value is None:
            return _('[no data]')

        total_seconds = value.days * 86400 + value.seconds + \
                value.microseconds / 1000000.0

        return _("%.2f sec.") % total_seconds


class ForeignKeySerializer(FieldSerializer):
    def __init__(self, field, other_serializer, *args, **kw):
        FieldSerializer.__init__(self, field=field, *args, **kw)
        self.other_serializer = other_serializer

    def serialize(self, model, output_format=None):
        other_model = self.extract_value(model)
        return self.other_serializer.serialize(
            other_model, output_format=output_format)

    def getFieldName(self):
        return self.field + "__" + self.other_serializer.getFieldName()


class URLSerializer(FieldSerializer):
    """Serializes model field to an URL. Useful for images.
    """

    urlName = None  # passed to self.resolver()
    resolver = None

    def __init__(self, field, urlName, resolver=None, *args, **kw):
        FieldSerializer.__init__(self, field, *args, **kw)
        self.urlName = urlName

        if resolver is not None:
            self.resolver = resolver

        if self.resolver is None:
            self.resolver = reverse

    def resolve(self, name, args):
        return self.resolver(name, args=args)

    def serialize_value(self, value, output_format=None):
        if value is None:
            return None
        return self.resolve(self.urlName, args = (value, ))


class HrefSerializer(FormatStringSerializer):
    """Serialize one of model's fields to a link. For JSON format,
    this is url[newline]value format.
    """
    def __init__(self, format, urlSerializer):
        FormatStringSerializer.__init__(self, format)
        self.urlSerializer = urlSerializer

    def serialize(self, model, output_format=None):
        string_value = FormatStringSerializer.serialize(
            self, model, output_format=output_format)

        if output_format != formats.JSON:
            return string_value

        url_value = self.urlSerializer.serialize(
            model, output_format=output_format)

        return '\n'.join([url_value, string_value])


# QuerySet serializers - a different sort of thing, than FieldSerializer
# they serialize querySets

class QuerySetSerializer:
    """I serialize sets, row by row, element by element, to a
    specific format.
    """

    output_format = None

    def __init__(self, columns):
        self.columns = columns

    def serializeModel(self, model):
        row = []
        for column in self.columns:
            row.append(
                (
                    column.getName(),
                    column.getSerializer().serialize(
                        model,
                        output_format = self.output_format
                    )
                )
            )
        return SortedDict(row)

    def serialize(self, querySet):
        for model in querySet:
            yield self.serializeModel(model)
