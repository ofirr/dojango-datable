"""
Test utility class for datable-enabled web pages.
"""

import csv
import json

import xlrd

from django.core.urlresolvers import reverse


class TestPageWithDatableMixin:

    tableName = None  # setup this
    urlName = None  # setup this
    indexCode = 200
    params = []  # list of dicts() with kw for jsonTest, xlsTest..

    def getURL(self):
        return reverse(self.urlName)

    def setUp(self):
        assert self.tableName, "Please set self.tableName for this class"
        assert self.urlName, "Please set self.urlName for this class"

    def bug(self, subs, err, kw, response):
        msg = "%(subs)s error: %(err)r while %(losubs)sTest with params: " \
              "%(kw)r url: %(url)r)"
        dct = dict(
            subs=subs, losubs=subs.lower(), err=err, kw=kw, url=self.getURL()
            )
        if response is not None:
            msg += "(content: %(content)r; HTTP code: %(code)r"
            dct.update(dict(
                content=response.content,
                code=response.status_code))
        raise Exception(msg % dct)

    def getDatable(self, format, **kw):
        kwargs = {self.tableName: format}
        kwargs.update(kw)
        return self.client.get(self.getURL(), kwargs)

    def getResponse(self, format, **kw):
        response = self.getDatable(format, **kw)
        if response.status_code != 200:
            self.bug(
                format,
                Exception("status_code!=200"),
                kw, response)
        return response

    def _jsonTest(self, response, name="json", **kw):
        value = response.content
        line = value.split('\n')[-1]
        try:
            json.loads(line)
        except Exception, err:
            self.bug(name, err, kw, response)

    def jsonTest(self, **kw):
        response = self.getResponse("json", **kw)
        return self._jsonTest(response, **kw)

    def xlsTest(self, **kw):
        try:
            response = self.getResponse("xls", **kw)
        except Exception, err:
            self.bug("xls-rendering", err, kw, None)
        try:
            xlrd.open_workbook(
                file_contents=response.content
                )
        except Exception, err:
            self.bug("xls", err, kw, response)

    def csvTest(self, **kw):
        response = self.getResponse("csv", **kw)
        try:
            csv.reader(response.content).next()
        except Exception, err:
            self.bug("csv", err, kw, response)

    def widgetTest(self, **kw):
        format = kw.pop('__format__')
        response = self.getResponse(format, **kw)
        return self._jsonTest(response, name="widget", **kw)

    def test_datable(self):
        assert self.params, "No test parameters"

        index = self.client.get(self.getURL())
        if index.status_code != self.indexCode:
            raise Exception('status_code for index %r != %r for URL %r' % (
                index.status_code, self.indexCode, self.getURL()
            ))

        for kwDict in self.params:
            if '__format__' in kwDict:
                if kwDict['__format__'].startswith('widget'):
                    self.widgetTest(**kwDict)
                    continue
                raise Exception("Unknown format: %r" % kwDict['__format__'])

            for subsystem in [self.xlsTest, self.jsonTest]:
                subsystem(**kwDict)
