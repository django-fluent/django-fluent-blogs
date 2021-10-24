from django.conf import settings
from django.urls import path, re_path

from fluent_blogs import appsettings
from fluent_blogs.views.entries import (
    EntryArchiveIndex,
    EntryAuthorArchive,
    EntryCategoryArchive,
    EntryDayArchive,
    EntryDetail,
    EntryMonthArchive,
    EntryShortLink,
    EntryTagArchive,
    EntryYearArchive,
)
from fluent_blogs.views.feeds import (
    LatestAuthorEntriesFeed,
    LatestCategoryEntriesFeed,
    LatestEntriesFeed,
    LatestTagEntriesFeed,
)


def _get_entry_regex():
    # Configurable permalink style!
    regex = (
        appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE.replace("{year}", r"(?P<year>\d{4})")
        .replace("{month}", r"(?P<month>\d{2})")
        .replace("{day}", r"(?P<day>\d{2})")
        .replace("{slug}", r"(?P<slug>[-\w]+)")
        .replace("{pk}", r"(?P<pk>[-\w]+)")
    )
    return "^{}$".format(regex.lstrip("/"))


urlpatterns = [
    # Index
    path("", EntryArchiveIndex.as_view(), name="entry_archive_index"),
    path("page/<int:page>/", EntryArchiveIndex.as_view(), name="entry_archive_index_paginated"),
    re_path(
        r"^feed.rss2$", LatestEntriesFeed.as_view(format="rss2.0"), name="entry_archive_index_rss"
    ),
    re_path(
        r"^feed.atom$", LatestEntriesFeed.as_view(format="atom1"), name="entry_archive_index_atom"
    ),
    # Archives
    re_path(r"^(?P<year>\d{4})/$", EntryYearArchive.as_view(), name="entry_archive_year"),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/$",
        EntryMonthArchive.as_view(),
        name="entry_archive_month",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$",
        EntryDayArchive.as_view(),
        name="entry_archive_day",
    ),
    # Categories
    re_path(
        r"^categories/(?P<slug>[-\w]+)/$",
        EntryCategoryArchive.as_view(),
        name="entry_archive_category",
    ),
    re_path(
        r"^categories/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$",
        EntryCategoryArchive.as_view(),
        name="entry_archive_category_paginated",
    ),
    re_path(
        r"^categories/(?P<slug>[-\w]+)/feed.rss2$",
        LatestCategoryEntriesFeed.as_view(format="rss2.0"),
        name="entry_archive_category_rss",
    ),
    re_path(
        r"^categories/(?P<slug>[-\w]+)/feed.atom$",
        LatestCategoryEntriesFeed.as_view(format="atom1"),
        name="entry_archive_category_atom",
    ),
    # Authors
    re_path(
        r"^authors/(?P<slug>[-_@.\w]+)/$",
        EntryAuthorArchive.as_view(),
        name="entry_archive_author",
    ),
    re_path(
        r"^authors/(?P<slug>[-_@.\w]+)/page/(?P<page>\d+)/$",
        EntryAuthorArchive.as_view(),
        name="entry_archive_author_paginated",
    ),
    re_path(
        r"^authors/(?P<slug>[-_@.\w]+)/feed.rss2$",
        LatestAuthorEntriesFeed.as_view(format="rss2.0"),
        name="entry_archive_author_rss",
    ),
    re_path(
        r"^authors/(?P<slug>[-_@.\w]+)/feed.atom$",
        LatestAuthorEntriesFeed.as_view(format="atom1"),
        name="entry_archive_author_atom",
    ),
    # Short link
    path(
        "<int:pk>/", EntryShortLink.as_view(), name="entry_shortlink"
    ),  # Short link can also be used as GUID.
    # Entries
    re_path(_get_entry_regex(), EntryDetail.as_view(), name="entry_detail"),
]


if "taggit" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^tags/(?P<slug>[-\w]+)/$", EntryTagArchive.as_view(), name="entry_archive_tag"),
        re_path(
            r"^tags/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$",
            EntryTagArchive.as_view(),
            name="entry_archive_tag_paginated",
        ),
        re_path(
            r"^tags/(?P<slug>[-\w]+)/feed.rss2$",
            LatestTagEntriesFeed.as_view(format="rss2.0"),
            name="entry_archive_tag_rss",
        ),
        re_path(
            r"^tags/(?P<slug>[-\w]+)/feed.atom$",
            LatestTagEntriesFeed.as_view(format="atom1"),
            name="entry_archive_tag_atom",
        ),
    ]
