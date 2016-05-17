from django.conf.urls import url, include
import fluent_blogs.urls

urlpatterns = [
    url(r'^blog/', include(fluent_blogs.urls)),
]
