"""
The manager class for the CMS models
"""
from django.db import models
from django.db.models.query import QuerySet


class EntryQuerySet(QuerySet):
    def published(self):
        """
        Return only published entries
        """
        from fluent_blogs.models import Entry   # the import can't be globally, that gives a circular dependency
        return self.filter(status=Entry.PUBLISHED)



class EntryManager(models.Manager):
    """
    Extra methods attached to ``Entry.objects`` .
    """
    def get_query_set(self):
        return EntryQuerySet(self.model, using=self._db)

    def published(self):
        """
        Return only published entries
        """
        return self.get_query_set().published()
