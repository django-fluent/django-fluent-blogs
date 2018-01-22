from django.conf.urls import url, include
from django.contrib import admin
import fluent_blogs.urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^blog/', include(fluent_blogs.urls)),
]
