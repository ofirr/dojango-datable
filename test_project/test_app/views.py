from datetime import datetime
from django.shortcuts import redirect

from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from datable.web.columns import HrefColumn
from datable.web.columns import ImageColumn

from datable.core.serializers import HrefSerializer
from datable.core.serializers import URLSerializer

from django.db.models import Q

from datable.web.table import Table
from datable.web.storage import Storage

from datable.core.converters import IntegerConverter
from datable.web.widgets import Maximum, Minimum
from datable.web.widgets import Constraints
from datable.web.widgets import Widget
from datable.web.widgets import StringWidget
from datable.web.widgets import BooleanWidget
from datable.web.widgets import DateWidget
from datable.web.widgets import DateTimeWidget

from datable.core.serializers import UnicodeSerializer
from datable.core.serializers import FormatStringSerializer
from datable.core.filters import IntegerFilter

from datable.web.extra.widgets import AutocompleteStringWidget
from datable.web.extra.widgets import DateTimeLessOrEqual
from datable.web.extra.widgets import ForeignKeyComboBox
from datable.web.extra.widgets import DateTimeGreaterOrEqual
from datable.web.extra.widgets import PeriodicRefreshWidget
from datable.core.converters import DojoComboValueConverter
from datable.core.filters import StringFilter

from datable.web.columns import Column
from datable.web.columns import StringColumn
from datable.web.columns import DateColumn
from datable.web.columns import BooleanColumn
from datable.web.columns import DateTimeColumn
from datable.core.serializers import ForeignKeySerializer
from datable.core.serializers import StringSerializer

from test_app import models


class AuthorsSerializer(UnicodeSerializer):
    """This is an implementation of a custom field serializer for a
    M2M relations with 'through'. In this example, what matters to us is
    the order of authors.
    """

    def serialize(self, model, output_format=None):
        return ", ".join([
            str(author)
            for author in model.authors.all().order_by('bookauthor__sort_order')
            ])


class AuthorStorageFilter(StringFilter):
    def enabled(self, querySet, safe_value):
        return querySet.filter(
            Q(last__contains=safe_value)
            | Q(first__contains=safe_value)
            )


def books_demo(request):

    first_table = Table(
        name='first_table',

        storage=Storage(
            querySet=models.Book.objects.all(),
            columns=[
                StringColumn('pk', width=100),
                StringColumn('title', width=350),
                DateColumn('published_on', width=100),
                DateTimeColumn('created_on', width=150),
                BooleanColumn('approved', width=30),
                Column(
                    'book_type__name',
                    width=100,
                    sortable=True,
                    serializer=ForeignKeySerializer(
                        'book_type',
                        StringSerializer(
                            'name'
                        )
                    )
                ),
                Column(
                    'authors',
                    width=100,
                    sortable=False,
                    serializer=AuthorsSerializer())
                ],
            widgets=[
                StringWidget('title', placeholder=_("Title")),
                DateWidget('published_on', placeholder=_('Published on')),
                DateTimeLessOrEqual('created_on', paired=True),
                DateTimeGreaterOrEqual('created_on', paired=True),

                PeriodicRefreshWidget('periodic', filterField='published_on'),

                BooleanWidget('approved', placeholder=_('Was approved before')),

                ForeignKeyComboBox(
                    'book_type', otherSet=models.BookType.objects.all(), otherField='name',
                    otherFormat='Book Type: %(name)s',
                    placeholder=_("book type")),

                Widget(
                    'authors',
                    placeholder=_("Authors"),
                    filter=IntegerFilter('bookauthor__author__pk'),
                    converter=IntegerConverter('authors', min=0),
                    templateName="autocomplete_string",
                    storage=Storage(
                        querySet=models.Author.objects.all(),
                        defaultSort='last',
                        columns=[
                            StringColumn(
                                'label',
                                serializer=FormatStringSerializer('%(last)s %(first)s')),
                            ],
                        widgets=[
                            Widget(
                                'label',
                                converter=DojoComboValueConverter('label'),
                                filter=AuthorStorageFilter('label'))
                        ]
                    )
                )


            ]
            ),
        filename=_("My important export data %Y-%m-%d")
        )

    if first_table.willHandle(request):
        return first_table.handleRequest(request)

    return render_to_response(
        "books.html", {'first_table': first_table})


def authors_demo(request):
    first_table = Table(
        name='first_table',

        storage=Storage(
            querySet=models.Author.objects.all(),

            columns=[
                StringColumn('pk', width=100),
                StringColumn('last', width=150),
                StringColumn('first', width=150),
                HrefColumn(
                    'author',
                    width=150,
                    sortable=False,
                    serializer=HrefSerializer(
                        "Check on Google",
                        FormatStringSerializer(
                            'https://www.google.com/search?q=%(last)s%%20%(first)s',
                        )
                    )
                )
            ],

            widgets=[
                StringWidget(
                    'author',
                    placeholder=_("Author"),
                    initialValue='joh',
                    # Filter reuse!
                    filter=AuthorStorageFilter('author')
                    ),
                AutocompleteStringWidget(
                    'first',
                    filter=AuthorStorageFilter('author'),
                    storage=Storage(
                        querySet=models.Author.objects.all().order_by('last'),
                        columns=[StringColumn('label', serializer=UnicodeSerializer())],
                        widgets=[Widget('label',
                            converter=DojoComboValueConverter('label'),
                            filter=StringFilter('pk', operation="eq")
                            )
                        ],
                    )
                )
                ]
            ),
        filename=_("My important export data %Y-%m-%d")
        )

    if first_table.willHandle(request):
        return first_table.handleRequest(request)

    return render_to_response(
        "authors.html", {'first_table': first_table})


def images_demo(request):
    imageTable = Table(
        name='imageTable',

        storage=Storage(
            querySet=models.Author.objects.all(),

            columns=[
                StringColumn('pk', width=100),
                StringColumn('last', width=150),
                ImageColumn(
                    'pk',
                    label='Random image',

                    serializer=URLSerializer(
                        "pk",
                        "images_server",
                    )
                )
            ],
        ),
    )

    if imageTable.willHandle(request):
        return imageTable.handleRequest(request)

    return render_to_response(
        "images.html", {'imageTable': imageTable})


def images_server(request, num):
    return redirect('http://farm8.staticflickr.com/7009/6560069937_351e34dd34_m.jpg')
