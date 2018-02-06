from django.conf import settings
from django.conf.urls import url
from fluent_blogs.views.entries import EntryArchiveIndex, EntryYearArchive, EntryMonthArchive, EntryDayArchive, EntryDetail, EntryShortLink, EntryCategoryArchive, EntryAuthorArchive, EntryTagArchive
from fluent_blogs.views.feeds import LatestEntriesFeed, LatestCategoryEntriesFeed, LatestAuthorEntriesFeed, LatestTagEntriesFeed
from fluent_blogs import appsettings


def _get_entry_regex():
    # Configurable permalink style!
    regex = appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE \
        .replace('{year}', r'(?P<year>\d{4})') \
        .replace('{month}', r'(?P<month>\d{2})') \
        .replace('{day}', r'(?P<day>\d{2})') \
        .replace('{slug}', r'(?P<slug>[-\w]+)') \
        .replace('{pk}', r'(?P<pk>[-\w]+)')
    return '^{0}$'.format(regex.lstrip('/'))


urlpatterns = [
    # Index
    url(r'^$', EntryArchiveIndex.as_view(), name='entry_archive_index'),
    url(r'^page/(?P<page>\d+)/$', EntryArchiveIndex.as_view(), name='entry_archive_index_paginated'),
    url(r'^feed.rss2$', LatestEntriesFeed.as_view(format='rss2.0'), name='entry_archive_index_rss'),
    url(r'^feed.atom$', LatestEntriesFeed.as_view(format='atom1'), name='entry_archive_index_atom'),

    # Archives
    url(r'^(?P<year>\d{4})/$', EntryYearArchive.as_view(), name='entry_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', EntryMonthArchive.as_view(), name='entry_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', EntryDayArchive.as_view(), name='entry_archive_day'),

    # Categories
    url(r'^categories/(?P<slug>[-\w]+)/$', EntryCategoryArchive.as_view(), name='entry_archive_category'),
    url(r'^categories/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', EntryCategoryArchive.as_view(), name='entry_archive_category_paginated'),
    url(r'^categories/(?P<slug>[-\w]+)/feed.rss2$', LatestCategoryEntriesFeed.as_view(format='rss2.0'), name='entry_archive_category_rss'),
    url(r'^categories/(?P<slug>[-\w]+)/feed.atom$', LatestCategoryEntriesFeed.as_view(format='atom1'), name='entry_archive_category_atom'),

    # Authors
    url(r'^authors/(?P<slug>[-_@.\w]+)/$', EntryAuthorArchive.as_view(), name='entry_archive_author'),
    url(r'^authors/(?P<slug>[-_@.\w]+)/page/(?P<page>\d+)/$', EntryAuthorArchive.as_view(), name='entry_archive_author_paginated'),
    url(r'^authors/(?P<slug>[-_@.\w]+)/feed.rss2$', LatestAuthorEntriesFeed.as_view(format='rss2.0'), name='entry_archive_author_rss'),
    url(r'^authors/(?P<slug>[-_@.\w]+)/feed.atom$', LatestAuthorEntriesFeed.as_view(format='atom1'), name='entry_archive_author_atom'),

    # Short link
    url(r'^(?P<pk>\d+)/$', EntryShortLink.as_view(), name='entry_shortlink'),   # Short link can also be used as GUID.

    # Entries
    url(_get_entry_regex(), EntryDetail.as_view(), name='entry_detail'),
]


if 'taggit' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^tags/(?P<slug>[-\w]+)/$', EntryTagArchive.as_view(), name='entry_archive_tag'),
        url(r'^tags/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', EntryTagArchive.as_view(), name='entry_archive_tag_paginated'),
        url(r'^tags/(?P<slug>[-\w]+)/feed.rss2$', LatestTagEntriesFeed.as_view(format='rss2.0'), name='entry_archive_tag_rss'),
        url(r'^tags/(?P<slug>[-\w]+)/feed.atom$', LatestTagEntriesFeed.as_view(format='atom1'), name='entry_archive_tag_atom'),
    ]
