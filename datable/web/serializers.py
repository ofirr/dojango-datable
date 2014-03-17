
from dojango.util import to_dojo_data

from datable.core import formats
from datable.core.serializers import QuerySetSerializer

from cStringIO import StringIO

import xlwt
import csv

class JSONQuerySetSerializer(QuerySetSerializer):
    output_format = formats.JSON
    identifier = 'pk'

    def __init__(self, *args, **kw):
        QuerySetSerializer.__init__(self, *args, **kw)

    def serializeModel(self, model):
        result = QuerySetSerializer.serializeModel(self, model)
        result[self.identifier] = getattr(model, self.identifier)
        return result

    def serialize(self, querySet, totalRows):
        return to_dojo_data(
            list(QuerySetSerializer.serialize(self, querySet)),
            identifier=self.identifier,
            num_rows=totalRows)

class XLSQuerySetSerializer(QuerySetSerializer):
    output_format = formats.XLS

    def serialize(self, querySet, title, header, exportDescription):
        """Serialize data to XLS.
        XXX: TODO: Currently, this is memory-inefficient.
        """
        book = xlwt.Workbook(encoding='utf-8')
        sheet = book.add_sheet(title)

        cur_row = 0

        for row in exportDescription:
            for col_no, col in enumerate(row):
                sheet.write(cur_row, col_no, col)
            cur_row += 1

        cur_row += 1

        for col_no, col in enumerate(header):
            sheet.write(cur_row, col_no, header[col_no])

        for row_no, row in enumerate(
            QuerySetSerializer.serialize(self, querySet)):
            for col_no, col in enumerate(row.keys()):
                sheet.write(cur_row + row_no + 1, col_no, row[col])

        output = StringIO()
        book.save(output)
        output.seek(0)
        return output


class CSVQuerySetSerializer(QuerySetSerializer):
    output_format = formats.CSV

    def serialize(self, querySet, title, header, exportDescription):
        """Serialize data to CSV
        XXX: TODO: Currently, this is memory-inefficient.
        """
        a = StringIO()
        csv_writer = csv.writer(a)

        for row in exportDescription:
            csv_writer.writerow(row)

        csv_writer.writerow([unicode(v).encode('utf8') for v in header])

        for elem in QuerySetSerializer.serialize(self, querySet):
            csv_writer.writerow(
                [unicode(v).encode('utf8') for v in elem.values()])

        a.seek(0)
        return a
