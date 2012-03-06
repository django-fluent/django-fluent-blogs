from django.conf import settings
from django.conf.urls.defaults import patterns, url
from fluent_blogs.views import EntryArchiveIndex, EntryYearArchive, EntryMonthArchive, EntryDayArchive, EntryDetail, EntryShortLink, EntryCategoryArchive, EntryAuthorArchive
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


urlpatterns = patterns('',
    # Index
    url(r'^$', EntryArchiveIndex.as_view(), name='entry_archive_index'),
    url(r'^page/(?P<page>\d+)/$', EntryArchiveIndex.as_view(), name='entry_archive_index_paginated'),

    # Archives
    url(r'^(?P<year>\d{4})/$', EntryYearArchive.as_view(), name='entry_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', EntryMonthArchive.as_view(), name='entry_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', EntryDayArchive.as_view(), name='entry_archive_day'),

    # Categories
    url(r'^categories/(?P<slug>[-\w]+)/$', EntryCategoryArchive.as_view(), name='entry_archive_category'),
    url(r'^categories/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', EntryCategoryArchive.as_view(), name='entry_archive_category_paginated'),

    # Authors
    url(r'^authors/(?P<slug>[-\w]+)/$', EntryAuthorArchive.as_view(), name='entry_archive_author'),
    url(r'^authors/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', EntryAuthorArchive.as_view(), name='entry_archive_author_paginated'),

    # Entries
    url(r'^(?P<pk>\d+)/$', EntryShortLink.as_view(), name='entry_shortlink'),
    url(_get_entry_regex(), EntryDetail.as_view(), name='entry_detail'),
)


if 'taggit' in settings.INSTALLED_APPS:
    from fluent_blogs.views import EntryTagArchive

    urlpatterns += patterns('',
        url(r'^tags/(?P<slug>[-\w]+)/$', EntryTagArchive.as_view(), name='entry_archive_tag'),
        url(r'^tags/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', EntryTagArchive.as_view(), name='entry_archive_tag_paginated'),
    )
