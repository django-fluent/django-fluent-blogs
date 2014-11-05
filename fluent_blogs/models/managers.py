"""
The manager class for the CMS models
"""
import django
from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.timezone import now
from fluent_blogs import appsettings
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

    def tagged(self, *tag_slugs):
        """
        Return the items which are tagged with a specific tag.
        When multiple tags are provided, they operate as "OR" query.
        """
        if getattr(self.model, 'tags', None) is None:
            raise AttributeError("The {0} does not include TagsEntryMixin".format(self.model.__name__))

        qs = self.filter(tags__slug__in=tag_slugs)
        if len(tag_slugs) > 1:
            qs = qs.distinct()

        return qs



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

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def parent_site(self, site):
        """
        Filter to the given site.
        """
        # NOTE: by using .all(), the correct get_queryset() or get_query_set() method is called.
        # Just calling self.get_queryset() will break the RelatedManager.get_query_set() override in Django 1.5
        # This avoids all issues with Django 1.5/1.6/1.7 compatibility.
        return self.all().parent_site(site)

    def published(self):
        """
        Return only published entries for the current site.
        """
        return self.all().published()

    def tagged(self, *tag_slugs):
        """
        Return the items which are tagged with a specific tag.
        When multiple tags are provided, they operate as "OR" query.
        """
        return self.all().tagged(*tag_slugs)


class TranslatableEntryManager(EntryManager, TranslatableManager):
    """
    Extra methods attached to ``Entry.objects``.
    """
    queryset_class = TranslatableEntryQuerySet
