from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

import fluent_pages.urls

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'', include(fluent_pages.urls)),
)
