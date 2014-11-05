from os.path import join, dirname
from example_standalone.settings import *

PARLER_DEFAULT_LANGUAGE_CODE = 'en'  # defaults to LANGUAGE_CODE

INSTALLED_APPS += (
    'debugtools',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'example_multilingual.context_processors.multilingual',
)

SITE_ID = 1

PARLER_LANGUAGES = {
    # site ID 1:
    1: (
        {'code': 'en'},
        {'code': 'fr'},
        {'code': 'de'},
        {'code': 'es'},
        {'code': 'nl'},
    ),
    'default': {
        'hide_untranslated': False,  # being explicit here.
        'fallback': 'en',            # defaults to PARLER_DEFAULT_LANGUAGE_CODE or LANGUAGE_CODE
    }
}

# NOTE: this middleware is not required, you can also use our own variation to set the frontend language.
MIDDLEWARE_CLASSES += (
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'example_multilingual.urls'

TEMPLATE_DIRS = (
    join(dirname(__file__), "templates"),
)
