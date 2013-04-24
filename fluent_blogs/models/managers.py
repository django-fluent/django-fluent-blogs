"""
The manager class for the CMS models
"""
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from fluent_blogs.utils.compat import now


class EntryQuerySet(QuerySet):
    def published(self):
        """
        Return only published entries
        """
        return self \
            .filter(status=self.model.PUBLISHED) \
            .filter(
                Q(publication_date__isnull=True) |
                Q(publication_date__lte=now())
            ).filter(
                Q(publication_end_date__isnull=True) |
                Q(publication_end_date__gte=now())
            )



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
