from django.db import models


class BookType(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Author(models.Model):
    first = models.CharField(max_length=255)
    last = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s %s" % (self.last, self.first)


class Book(models.Model):
    title = models.CharField(max_length=255,db_index=True)
    desc = models.CharField(max_length=255)
    book_type = models.ForeignKey(BookType,db_index=True)
    authors = models.ManyToManyField(Author, through='BookAuthor')

    published_on = models.DateField(db_index=True)

    created_on = models.DateTimeField(auto_now_add=True,db_index=True)

    approved = models.BooleanField(db_index=True)


class BookAuthor(models.Model):
    book = models.ForeignKey(Book)
    author = models.ForeignKey(Author)
    sort_order = models.IntegerField(default=0)
