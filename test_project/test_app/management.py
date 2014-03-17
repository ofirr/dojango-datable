import datetime
import os
import random


from django.db.models import signals
from django.db import transaction

from test_app.models import Author
from test_app.models import Book
from test_app.models import BookAuthor
from test_app.models import BookType

DEMO_DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    'demo_data')


def demo_file(name):
    return open(
        os.path.join(DEMO_DATA_PATH, name + '.txt'), 'r')


def demo_reader(name):
    f = demo_file(name)
    for line in f.readlines():
        try:
            yield line.decode('utf-8').strip()
        except:
            print line


@transaction.commit_on_success
def create_demo_data(**kwargs):
    """Create some random data. Why not fixtures? Well, we are
    more flexible this way and we can generate some random information
    too."""

    if Author.objects.all().count() == 0:

        for line in demo_reader('authors'):
            split = line.encode('utf-8').split(" ")
            Author.objects.create(
                first=" ".join(split[:-1]),
                last=split[-1])

    if BookType.objects.all().count() == 0:

        for line in demo_reader('types'):
            BookType.objects.create(name=line.strip())

    all_authors = list(Author.objects.all())
    all_types = list(BookType.objects.all())

    if Book.objects.all().count() == 0:

        for line in demo_reader('titles'):
            book = Book.objects.create(
                title=line,
                desc="Description of book named %s" % line,
                book_type=random.choice(all_types),
                published_on=datetime.date(
                    datetime.datetime.now().year,
                    datetime.datetime.now().month,
                    random.randint(1, 28)
                ),
                approved=[True,False][random.randint(0, 1)]
            )

            seen = set([None])

            for cnt in range(random.randint(1, 5)):

                author = None
                while author in seen:
                    author = random.choice(all_authors)
                seen.add(author)

                BookAuthor.objects.create(
                    book=book,
                    author=author,
                    sort_order=cnt)


signals.post_syncdb.connect(create_demo_data)
