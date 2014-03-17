import json

from datetime import datetime
from urllib import urlencode

from datable import core

from datable.core.serializers import PrimaryKeySerializer

from datable.web.serializers import JSONQuerySetSerializer
from datable.web.serializers import CSVQuerySetSerializer
from datable.web.serializers import XLSQuerySetSerializer

from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

class Storage:
    """I can filter a querySet using widgets;
    I can serialize it to various formats.
    """

    primaryKeySerializer = None
    defaultSort = None

    def __init__(self, querySet, columns, widgets=None, title='Sheet',
                 primaryKeySerializer=None, defaultSort=None):
        self.querySet = querySet

        self.columns = columns

        self.widgets = widgets

        if self.widgets is None:
            self.widgets = []

        self.title = title

        if primaryKeySerializer is not None:
            self.primaryKeySerializer = primaryKeySerializer

        if self.primaryKeySerializer is None:
            self.primaryKeySerializer = PrimaryKeySerializer()

        if defaultSort is not None:
            desc = False
            if defaultSort.startswith('-'):
                desc = True
                defaultSort = defaultSort[1:]

            col = self.getColumn(defaultSort)
            if col:
                self.defaultSort = col, desc


    def filterAndSort(self, valueDict, order_by):
        querySet = self.querySet
        for widget in self.widgets:
            querySet = widget.filterQuerySet(querySet, valueDict)

        if not order_by:
            order_by = self.defaultSort

        if order_by:
            querySet = order_by[0].sortQuerySet(querySet, order_by[1])

        return querySet

    def getWidgets(self):
        return self.widgets

    def getWidget(self, name):
        for widget in self.widgets:
            if widget.getName() == name:
                return widget

    def getColumns(self):
        return self.columns

    def getColumn(self, name):
        idx = self.getColumnIndex(name)
        if idx is None:
            return None
        return self.columns[idx]

    def getColumnIndex(self, name):
        for no, column in enumerate(self.columns):
            if column.getName() == name:
                return no

    def getSerializers(self):
        return [c.getSerializer() for c in self.columns]

    def getHeader(self):
        return [c.getLabel() for c in self.columns]

    def describeExportData(self, valueDict):
        """Few rows of description for an export file - when was the file
        generated, which filters were used.
        """

        yield _("Exported on"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for w in self.widgets:
            d = w.exportDescription(valueDict)
            if d is not None:
                yield d

    def serializeToJSON(self, valueDict, order_by):
        querySet = self.filterAndSort(valueDict, order_by)
        start = int(valueDict.get('start', 0))
        try:
            count = int(valueDict.get('count', 0)) or None
        except (TypeError, ValueError):
            count = None

        end = None
        if count is not None:
            end = start + count
        totalRows = querySet.count()

        return JSONQuerySetSerializer(
            columns=self.getColumns()
            ).serialize(querySet[start:end], totalRows)

    def serializeToCSV(self, valueDict, order_by):
        querySet = self.filterAndSort(valueDict, order_by)

        data = CSVQuerySetSerializer(
            columns=self.getColumns()
        ).serialize(
            querySet,
            self.title,
            self.getHeader(),
            self.describeExportData(valueDict)
        )
        data.seek(0)
        return data

    def serializeToXLS(self, valueDict, order_by):
        querySet = self.filterAndSort(valueDict, order_by)

        data = XLSQuerySetSerializer(
            columns=self.getColumns()
        ).serialize(
            querySet,
            self.title,
            self.getHeader(),
            self.describeExportData(valueDict)
        )
        data.seek(0)
        return data
