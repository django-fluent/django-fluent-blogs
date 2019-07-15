from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^admin/apps/tinymce/', include('tinymce.urls')),
    url(r'^admin/apps/tags/', include('taggit_autosuggest.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^comments/', include('fluent_comments.urls')),
    #url(r'^forms/', include('form_designer.urls')),

    url(r'', include('fluent_blogs.urls')),
]
