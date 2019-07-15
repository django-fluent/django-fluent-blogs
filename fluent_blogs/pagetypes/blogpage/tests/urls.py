import fluent_pages.urls
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'', include(fluent_pages.urls)),
)
