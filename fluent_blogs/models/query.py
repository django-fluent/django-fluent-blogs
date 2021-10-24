"""
A query interface to retrieve blog models and tags.
"""
import sys
from calendar import monthrange
from datetime import datetime, timedelta

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from django.utils.timezone import utc
from parler.models import TranslatableModel

from fluent_blogs import appsettings
from fluent_blogs.models.db import get_category_model, get_entry_model

if sys.version_info[0] >= 3:
    basestring = str


__all__ = (
    "query_entries",
    "query_tags",
)

ENTRY_ORDER_BY_FIELDS = {
    "slug": "slug",
    "title": "title",
    "author": ("author__first_name", "author__last_name"),
    "author_slug": ("author__username",),
    "category": ("categories__name",),
    "category_slug": ("categories__slug",),
    "tag": ("tags__name",),
    "tag_slug": ("tags__slug",),
    "date": ("publication_date",),
    "year": ("publication_date",),
}

if django.VERSION >= (1, 11):
    # Django 1.10 doesn't support early importing.
    User = get_user_model()
    ENTRY_ORDER_BY_FIELDS["author_slug"] = f"author__{User.USERNAME_FIELD}"

TAG_ORDER_BY_FIELDS = {
    "slug": ("slug",),
    "name": ("name",),
    "count": ("count",),
}

ORDER_BY_DESC = (
    "date",
    "year",
    "month",
    "day",
    "count",
)


def _get_order_by(order, orderby, order_by_fields):
    """
    Return the order by syntax for a model.
    Checks whether use ascending or descending order, and maps the fieldnames.
    """
    try:
        # Find the actual database fieldnames for the keyword.
        db_fieldnames = order_by_fields[orderby]
    except KeyError:
        raise ValueError(
            "Invalid value for 'orderby': '{}', supported values are: {}".format(
                orderby, ", ".join(sorted(order_by_fields.keys()))
            )
        )

    # Default to descending for some fields, otherwise be ascending
    is_desc = (not order and orderby in ORDER_BY_DESC) or (order or "asc").lower() in (
        "desc",
        "descending",
    )

    if is_desc:
        return map(lambda name: "-" + name, db_fieldnames)
    else:
        return db_fieldnames


def query_entries(
    queryset=None,
    year=None,
    month=None,
    day=None,
    category=None,
    category_slug=None,
    tag=None,
    tag_slug=None,
    author=None,
    author_slug=None,
    future=False,
    order=None,
    orderby=None,
    limit=None,
):
    """
    Query the entries using a set of predefined filters.
    This interface is mainly used by the ``get_entries`` template tag.
    """
    if queryset is None:
        queryset = get_entry_model().objects.all()

    if appsettings.FLUENT_BLOGS_FILTER_SITE_ID:
        queryset = queryset.parent_site(settings.SITE_ID)

    if not future:
        queryset = queryset.published()

    if year:
        queryset = queryset.filter(publication_date__year=year)
    if month:
        queryset = queryset.filter(publication_date__month=month)
    if day:
        queryset = queryset.filter(publication_date__day=day)

    # The main category/tag/author filters
    if category:
        if isinstance(category, basestring):
            queryset = queryset.categories(category)
        elif isinstance(category, (int, long)):
            queryset = queryset.filter(categories=category)
        else:
            raise ValueError("Expected slug or ID for the 'category' parameter")
    if category_slug:
        queryset = queryset.categories(category)

    if tag:
        if isinstance(tag, basestring):
            queryset = queryset.tagged(tag)
        elif isinstance(tag, (int, long)):
            queryset = queryset.filter(tags=tag)
        else:
            raise ValueError("Expected slug or ID for 'tag' parameter.")
    if tag_slug:
        queryset = queryset.tagged(tag)

    if author:
        if isinstance(author, basestring):
            queryset = queryset.authors(author)
        elif isinstance(author, (int, long)):
            queryset = queryset.filter(author=author)
        else:
            raise ValueError("Expected slug or ID for 'author' parameter.")
    if author_slug:
        queryset = queryset.authors(author_slug)

    # Ordering
    if orderby:
        queryset = queryset.order_by(*_get_order_by(order, orderby, ENTRY_ORDER_BY_FIELDS))
    else:
        queryset = queryset.order_by("-publication_date")

    # Limit
    if limit:
        queryset = queryset[:limit]

    return queryset


def query_tags(order=None, orderby=None, limit=None):
    """
    Query the tags, with usage count included.
    This interface is mainly used by the ``get_tags`` template tag.
    """
    from taggit.models import Tag, TaggedItem  # feature is still optional

    # Get queryset filters for published entries
    EntryModel = get_entry_model()
    ct = ContentType.objects.get_for_model(EntryModel)  # take advantage of local caching.

    entry_filter = {"status": EntryModel.PUBLISHED}
    if appsettings.FLUENT_BLOGS_FILTER_SITE_ID:
        entry_filter["parent_site"] = settings.SITE_ID

    entry_qs = EntryModel.objects.filter(**entry_filter).values_list("pk")

    # get tags
    queryset = Tag.objects.filter(
        taggit_taggeditem_items__content_type=ct, taggit_taggeditem_items__object_id__in=entry_qs
    ).annotate(count=Count("taggit_taggeditem_items"))

    # Ordering
    if orderby:
        queryset = queryset.order_by(*_get_order_by(order, orderby, TAG_ORDER_BY_FIELDS))
    else:
        queryset = queryset.order_by("-count")

    # Limit
    if limit:
        queryset = queryset[:limit]

    return queryset


def get_category_for_slug(slug, language_code=None):
    """
    Find the category for a given slug
    """
    Category = get_category_model()
    if issubclass(Category, TranslatableModel):
        return Category.objects.active_translations(language_code, slug=slug).get()
    else:
        return Category.objects.get(slug=slug)


def get_date_range(year=None, month=None, day=None):
    """
    Return a start..end range to query for a specific month, day or year.
    """
    if year is None:
        return None

    if month is None:
        # year only
        start = datetime(year, 1, 1, 0, 0, 0, tzinfo=utc)
        end = datetime(year, 12, 31, 23, 59, 59, 999, tzinfo=utc)
        return (start, end)

    if day is None:
        # year + month only
        start = datetime(year, month, 1, 0, 0, 0, tzinfo=utc)
        end = start + timedelta(days=monthrange(year, month)[1], microseconds=-1)
        return (start, end)
    else:
        # Exact day
        start = datetime(year, month, day, 0, 0, 0, tzinfo=utc)
        end = start + timedelta(days=1, microseconds=-1)
        return (start, end)
