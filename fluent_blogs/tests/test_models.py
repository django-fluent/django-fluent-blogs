from django.test import TestCase

from fluent_blogs.models import Entry, get_entry_model


class ModelTests(TestCase):
    def test_get_entry_model(self):
        self.assertIs(get_entry_model(), Entry)
