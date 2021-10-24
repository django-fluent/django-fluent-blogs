from django.contrib import admin
from django.urls import include, path

admin.autodiscover()

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/apps/tinymce/", include("tinymce.urls")),
    path("admin/apps/tags/", include("taggit_autosuggest.urls")),
    path("admin/", admin.site.urls),
    path("comments/", include("django_comments.urls")),
    # url(r'^forms/', include('form_designer.urls')),
    path("", include("fluent_blogs.urls")),
]
