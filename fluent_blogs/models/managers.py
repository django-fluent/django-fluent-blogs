"""
The manager class for the CMS models
"""
from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from fluent_blogs import appsettings
from fluent_blogs.utils.compat import now
from parler.managers import TranslatableManager, TranslatableQuerySet


class EntryQuerySet(QuerySet):
    """
    The QuerySet for entry models.
    """
    def parent_site(self, site):
        """
        Filter to the given site.
        """
        return self.filter(parent_site=site)

    def published(self):
        """
        Return only published entries for the current site.
        """
        if appsettings.FLUENT_BLOGS_FILTER_SITE_ID:
            qs = self.parent_site(settings.SITE_ID)
        else:
            qs = self

        return qs \
            .filter(status=self.model.PUBLISHED) \
            .filter(
                Q(publication_date__isnull=True) |
                Q(publication_date__lte=now())
            ).filter(
                Q(publication_end_date__isnull=True) |
                Q(publication_end_date__gte=now())
            )



class TranslatableEntryQuerySet(TranslatableQuerySet, EntryQuerySet):
    def active_translations(self, language_code=None, **translated_fields):
        # overwritten to honor our settings instead of the django-parler defaults
        language_codes = appsettings.FLUENT_BLOGS_LANGUAGES.get_active_choices(language_code)
        return self.translated(*language_codes, **translated_fields)


class EntryManager(models.Manager):
    """
    Extra methods attached to ``Entry.objects`` .
    """
    queryset_class = EntryQuerySet

    def get_query_set(self):
        return self.queryset_class(self.model, using=self._db)

    def parent_site(self, site):
        """
        Filter to the given site.
        """
        return self.get_query_set().parent_site(site)

    def published(self):
        """
        Return only published entries for the current site.
        """
        return self.get_query_set().published()


class TranslatableEntryManager(EntryManager, TranslatableManager):
    """
    Extra methods attached to ``Entry.objects``.
    """
    queryset_class = TranslatableEntryQuerySet
