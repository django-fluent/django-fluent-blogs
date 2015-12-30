from django.conf.urls import include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/apps/tinymce/', include('tinymce.urls')),
    url(r'^admin/apps/tags/', include('taggit_autosuggest.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^comments/', include('django.contrib.comments.urls')),
    #url(r'^forms/', include('form_designer.urls')),

    url(r'', include('fluent_blogs.urls')),
]
