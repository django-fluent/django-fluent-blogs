import django

from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

import fluent_pages.urls

if django.VERSION >= (1, 8):
    urlpatterns = i18n_patterns(
        url(r'^admin/', include(admin.site.urls)),
        url(r'', include(fluent_pages.urls)),
    )
else:
    urlpatterns = i18n_patterns('',  # prefix
        url(r'^admin/', include(admin.site.urls)),
        url(r'', include(fluent_pages.urls)),
    )
