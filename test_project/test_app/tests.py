#

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from datable.testutil import TestPageWithDatableMixin


class TestBooks(TestPageWithDatableMixin, TestCase):

    tableName = 'first_table'
    urlName = 'books_demo'

    def setUp(self):
        super(TestBooks, self).setUp()
        self.client = Client()

    params = [
        dict(),
        dict(sort='title'),
        dict(sort='-title'),
        dict(__format__='widget,book_type'),
        dict(__format__='widget,book_type', f='sci'),
        dict(__format__='widget,authors'),
        dict(__format__='widget,authors', f='brown'),
        dict(periodic='true'),
        dict(approved='true'),
    ]


class TestAuthors(TestBooks):

    tableName = 'first_table'
    urlName = 'authors_demo'

    params = [
        dict(),
        dict(start=0, count=25, author='asf'),
        dict(sort='last'),
        dict(sort='-last'),
        dict(sort='first'),
        dict(sort='-first'),
        dict(sort='authors'),
        dict(sort='authors'),
    ]


class TestInitialValues(TestCase):
    def test_initialValues(self):
        client = Client()
        res = client.get(reverse('authors_demo'))
        self.assertContains(res, "first_tableGridFilter['author'] = 'joh';")
