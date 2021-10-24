"""
The manager class for the CMS models
"""
from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.utils.timezone import now
from parler.managers import TranslatableManager, TranslatableQuerySet
from parler.models import TranslatableModel

from fluent_blogs import appsettings


class EntryQuerySet(QuerySet):
    """
    The QuerySet for entry models.
    """

    def parent_site(self, site):
        """
        Filter to the given site.
        """
        return self.filter(parent_site=site)

    def published(self, for_user=None, include_hidden=False):
        """
        Return only published entries for the current site.
        """
        if appsettings.FLUENT_BLOGS_FILTER_SITE_ID:
            qs = self.parent_site(settings.SITE_ID)
        else:
            qs = self

        if for_user is not None and for_user.is_staff:
            return qs

        if include_hidden:
            filters = Q(status__in=(self.model.PUBLISHED, self.model.HIDDEN))
        else:
            filters = Q(status=self.model.PUBLISHED)

        filters &= (Q(publication_date__isnull=True) | Q(publication_date__lte=now())) & (
            Q(publication_date__isnull=True) | Q(publication_date__lte=now())
        )

        return qs.filter(filters)

    def authors(self, *usernames):
        """
        Return the entries written by the given usernames
        When multiple tags are provided, they operate as "OR" query.
        """
        if len(usernames) == 1:
            return self.filter(**{f"author__{User.USERNAME_FIELD}": usernames[0]})
        else:
            return self.filter(**{f"author__{User.USERNAME_FIELD}__in": usernames})

    def categories(self, *category_slugs):
        """
        Return the entries with the given category slugs.
        When multiple tags are provided, they operate as "OR" query.
        """
        categories_field = getattr(self.model, "categories", None)
        if categories_field is None:
            raise AttributeError(
                f"The {self.model.__name__} does not include CategoriesEntryMixin"
            )

        if issubclass(categories_field.rel.model, TranslatableModel):
            # Needs a different field, assume slug is translated (e.g django-categories-i18n)
            filters = {
                "categories__translations__slug__in": category_slugs,
            }

            # TODO: should the current language also be used as filter somehow?
            languages = self._get_active_rel_languages()
            if languages:
                if len(languages) == 1:
                    filters["categories__translations__language_code"] = languages[0]
                else:
                    filters["categories__translations__language_code__in"] = languages

            return self.filter(**filters).distinct()
        else:
            return self.filter(categories__slug=category_slugs)

    def tagged(self, *tag_slugs):
        """
        Return the items which are tagged with a specific tag.
        When multiple tags are provided, they operate as "OR" query.
        """
        if getattr(self.model, "tags", None) is None:
            raise AttributeError(f"The {self.model.__name__} does not include TagsEntryMixin")

        if len(tag_slugs) == 1:
            return self.filter(tags__slug=tag_slugs[0])
        else:
            return self.filter(tags__slug__in=tag_slugs).distinct()

    def _get_active_rel_languages(self):
        return ()


class TranslatableEntryQuerySet(TranslatableQuerySet, EntryQuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rel_language_codes = None

    def _clone(self, *args, **kw):
        c = super(TranslatableQuerySet, self)._clone(*args, **kw)
        c._rel_language_codes = self._rel_language_codes
        return c

    def active_translations(self, language_code=None, **translated_fields):
        # overwritten to honor our settings instead of the django-parler defaults
        language_codes = appsettings.FLUENT_BLOGS_LANGUAGES.get_active_choices(language_code)
        return self.translated(*language_codes, **translated_fields)

    def translated(self, *language_codes, **translated_fields):
        self._rel_language_codes = language_codes
        return super().translated(*language_codes, **translated_fields)

    def _get_active_rel_languages(self):
        return self._rel_language_codes


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
        return self.all().parent_site(site)

    def published(self, for_user=None, include_hidden=False):
        """
        Return only published entries for the current site.
        """
        return self.all().published(for_user=for_user, include_hidden=include_hidden)

    def authors(self, *usernames):
        """
        Return the entries written by the given usernames
        When multiple tags are provided, they operate as "OR" query.
        """
        return self.all().authors(*usernames)

    def categories(self, *category_slugs):
        """
        Return the entries with the given category slugs.
        When multiple tags are provided, they operate as "OR" query.
        """
        return self.all().categories(*category_slugs)

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
