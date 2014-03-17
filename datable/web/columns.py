# /usr/bin/env python
# -*- encoding: utf-8 -*-

from django.utils.text import capfirst
from django.utils.translation import ugettext as _

from datable.core.serializers import BooleanSerializer
from datable.core.serializers import DateSerializer
from datable.core.serializers import DateTimeSerializer
from datable.core.serializers import TimedeltaSerializer
from datable.core.serializers import StringSerializer

class Column(object):

    label = None
    width = None
    sortable = None
    serializer = None
    serializerClass = None
    formatter = None
    sortColumnName = None  # Parameter for QuerySet.order_by

    def __init__(self, name, label=None, width=None,
                 serializer=None, sortable=None, sortColumnName=None):

        self.name = name

        if label is not None:
            self.label = label

        if self.label is None:
            self.label = _(capfirst(self.name.replace("_", " ")))

        if width is not None:
            self.width = width

        if sortable is not None:
            self.sortable = sortable

        if serializer is not None:
            self.serializer = serializer

        if self.serializer is None:
            self.serializer = self.serializerClass(self.name)

        if sortColumnName is not None:
            self.sortColumnName = sortColumnName

        if self.sortColumnName is None and self.sortable:
            self.sortColumnName = name

    def sortQuerySet(self, querySet, desc):
        """The query set needs to be sorted using this column.
        """
        sort = self.sortColumnName
        if sort is None:
            raise Exception("This column can not be used to sort")
        if desc:
            sort = '-' + sort
        return querySet.order_by(sort)

    def getName(self):
        return self.name

    def getSerializer(self):
        return self.serializer

    def getLabel(self):
        return self.label

    def getFormatter(self):
        return self.formatter


class StringColumn(Column):
    serializerClass = StringSerializer
    sortable = True


class DateColumn(Column):
    serializerClass = DateSerializer
    sortable = True


class DateTimeColumn(Column):
    serializerClass = DateTimeSerializer
    sortable = True


class TimedeltaColumn(Column):
    serializerClass = TimedeltaSerializer
    sortable = True


class BooleanColumn(Column):
    serializerClass = BooleanSerializer
    sortable = True


class ImageColumn(Column):
    formatter = 'image'
    sortable = False


class HrefColumn(Column):
    formatter = 'href'
    sortable = False

