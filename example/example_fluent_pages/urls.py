from django.contrib import admin
from django.urls import include, path

admin.autodiscover()

urlpatterns = [
    path("admin/apps/tinymce/", include("tinymce.urls")),
    path("admin/apps/tags/", include("taggit_autosuggest.urls")),
    path("admin/", admin.site.urls),
    path("comments/", include("fluent_comments.urls")),
    # url(r'^forms/', include('form_designer.urls')),
    # Not including fluent_blogs.urls.
    # Instead, create a "blogpage" in the page tree.
    # all URLs will be displayed there.
    path("", include("fluent_pages.urls")),
]
