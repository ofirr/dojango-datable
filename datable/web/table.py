from django.http import HttpResponse
from django.http import Http404
from dojango.decorators import json_response
from django.utils.translation import ugettext as _

from datable.core import formats
from datetime import datetime
from urllib import urlencode

class Table(object):
    """A table, which may be presented as JSON or XLS or CSV.
    """

    filename = None
    columns = None
    widgets = None
    primaryKeySerializer = None

    def __init__(self, name, storage, filename=None):

        self.name = name
        self.storage = storage

        if filename is not None:
            self.filename = filename

        if self.filename is None:
            self.filename = self.name


    def getSortColumn(self, requestDict):
        real_name = requestDict.get('sort', None)

        if real_name is None:
            return

        desc = False

        if real_name[0] == '-':
            desc = True
            real_name = real_name[1:]

        for column in self.storage.getColumns():
            if real_name == column.getName():
                return column, desc

        return

    def filterAndSort(self, request, method="GET"):
        """This function performs filtering and sorting of a QuerySet,
        based on settings found in request, sent by method (POST, GET)"""
        requestDict = getattr(request, method)
        sortColumn = self.getSortColumn(requestDict)
        return self.storage.filterAndSort(requestDict, sortColumn)

    def getExportFilename(self, output_format):
        fn = u"%s.%s" % (self.filename, formats.getExtension(output_format))
        fn = datetime.now().strftime(fn.encode('utf-8')).replace(" ", "_")
        return urlencode([('filename', fn)])

    def fileResponse(self, fobj, output_format):
        # XXX: TODO: memory-intensive
        data = fobj.read()
        response = HttpResponse(data, mimetype=formats.getMimetype(output_format))
        cd = 'attachment; %s' % self.getExportFilename(output_format)
        response['Content-Disposition'] = cd
        response['Content-Length'] = len(data)
        return response

    def willHandle(self, request, method="GET"):
        """Will this datable handle this request?"""
        requestDict = getattr(request, method)
        if self.name in requestDict:
            return True

    @json_response
    def jsonResponse(self, data):
        return data

    def handleRequest(self, request, method="GET"):
        requestDict = getattr(request, method)
        order_by = self.getSortColumn(requestDict)

        param = requestDict.get(self.name)

        if param == 'json':
            return self.jsonResponse(
                self.storage.serializeToJSON(requestDict, order_by)
                )

        elif param == 'xls':
            return self.fileResponse(
                self.storage.serializeToXLS(requestDict, order_by),
                formats.XLS)

        elif param == 'csv':
            return self.fileResponse(
                self.storage.serializeToCSV(requestDict, order_by),
                formats.CSV)

        elif param.startswith('widget,'):
            widgetName = param.split(",")[1]
            w = self.storage.getWidget(widgetName)
            if not w:
                raise Http404

            other_storage = w.getStorage()

            if not other_storage:
                raise Http404

            valueDict = dict(requestDict.items())
            valueDict.pop(self.name)
            if 'sort' in valueDict:
                valueDict.pop('sort')

            return self.jsonResponse(other_storage.serializeToJSON(valueDict, None))

        raise Http404

    def getStorage(self):
        return self.storage
