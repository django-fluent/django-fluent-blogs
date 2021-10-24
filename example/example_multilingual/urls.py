from django.urls import include, path
from example_standalone.urls import urlpatterns

# Nothing needs to be changed for multilingual support really.
# It depends on the way your project is structured;
# whether you use i18n_patterns(), the LocaleMiddleware
# or separate settings per domain name with a different LANGUAGE_CODE set.

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
] + urlpatterns
