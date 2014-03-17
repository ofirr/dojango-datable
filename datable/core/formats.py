JSON = 0
XLS = 1
CSV = 2
HTML = 3

_extensions = {
    XLS: 'xls',
    CSV: 'csv',
    HTML: 'html'
}


_mimetypes = {
    XLS: 'application/vnd.ms-excel',
    CSV: 'text/csv',
    HTML: 'text/html'
}

class UnknownFormat(Exception):
    pass


def getExtension(output):
    return _extensions.get(output)


def getMimetype(output):
    return _mimetypes.get(output)
