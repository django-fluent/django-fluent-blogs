"""
The manager class for the CMS models
"""
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from fluent_blogs.utils.compat import now
from parler.managers import TranslatableManager, TranslatableQuerySet


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


class TranslatableEntryQuerySet(TranslatableQuerySet, EntryQuerySet):
    pass


class EntryManager(models.Manager):
    """
    Extra methods attached to ``Entry.objects`` .
    """
    queryset_class = EntryQuerySet

    def get_query_set(self):
        return self.queryset_class(self.model, using=self._db)

    def published(self):
        """
        Return only published entries
        """
        return self.get_query_set().published()


class TranslatableEntryManager(EntryManager, TranslatableManager):
    """
    Extra methods attached to ``Entry.objects``.
    """
    queryset_class = TranslatableEntryQuerySet
