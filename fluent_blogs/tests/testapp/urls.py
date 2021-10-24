from django.contrib import admin
from django.urls import include, path

import fluent_blogs.urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include(fluent_blogs.urls)),
]
