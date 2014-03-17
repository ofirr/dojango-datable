from datable.tests.test_columns import *
from datable.tests.test_core import *
from datable.tests.test_extra import *
from datable.tests.test_widgets import *
from datable.tests.test_views import *
from datable.tests.test_web import *

from django.test import TestCase

class TestDatableTags(TestCase):
    def test_datable_tags(self):
        from datable.templatetags import datable_tags
