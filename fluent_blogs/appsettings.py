from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from parler import appsettings as parler_appsettings
from parler.utils import normalize_language_code, is_supported_django_language


# Configurable permalink style, yeah!
FLUENT_BLOGS_ENTRY_LINK_STYLE = getattr(settings, "FLUENT_BLOGS_ENTRY_LINK_STYLE", '/{year}/{month}/{slug}/')

# Advanced settings
FLUENT_BLOGS_FILTER_SITE_ID = getattr(settings, 'FLUENT_BLOGS_FILTER_SITE_ID', True)
FLUENT_BLOGS_BASE_TEMPLATE = getattr(settings, "FLUENT_BLOGS_BASE_TEMPLATE", 'fluent_blogs/base.html')
FLUENT_BLOGS_CATEGORY_MODEL = getattr(settings, "FLUENT_BLOGS_CATEGORY_MODEL", 'categories.Category')
FLUENT_BLOGS_ENTRY_MODEL = getattr(settings, "FLUENT_BLOGS_ENTRY_MODEL", 'fluent_blogs.Entry')

# RSS feeds
FLUENT_BLOGS_FEED_PROTOCOL = getattr(settings, "FLUENT_BLOGS_FEED_PROTOCOL", 'http')
FLUENT_BLOGS_MAX_FEED_ITEMS = getattr(settings, "FLUENT_BLOGS_MAX_FEED_ITEMS", 30)

# Comment settings
FLUENT_BLOGS_INCLUDE_STATIC_FILES = getattr(settings, "FLUENT_BLOGS_INCLUDE_STATIC_FILES", True)

# Performance settings
FLUENT_BLOGS_PREFETCH_TRANSLATIONS = getattr(settings, 'FLUENT_BLOGS_PREFETCH_TRANSLATIONS', False)

# Note: the default language setting is used during the migrations
# Allow this module to have other settings, but default to the shared settings
FLUENT_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_DEFAULT_LANGUAGE_CODE', parler_appsettings.PARLER_DEFAULT_LANGUAGE_CODE)
FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE = getattr(settings, 'FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE', FLUENT_DEFAULT_LANGUAGE_CODE)
FLUENT_BLOGS_LANGUAGES = getattr(settings, 'FLUENT_BLOGS_LANGUAGES', parler_appsettings.PARLER_LANGUAGES)


# Clean settings
FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE = normalize_language_code(FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE)

if not is_supported_django_language(FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE):
    raise ImproperlyConfigured("FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE '{0}' does not exist in LANGUAGES".format(FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE))

FLUENT_BLOGS_LANGUAGES = parler_appsettings.add_default_language_settings(
    FLUENT_BLOGS_LANGUAGES, 'FLUENT_BLOGS_LANGUAGES',
    code=FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE,
    fallback=FLUENT_BLOGS_DEFAULT_LANGUAGE_CODE,
    hide_untranslated=False,
)


def get_language_settings(language_code, site_id=None):
    """
    Return the language settings for the current site
    """
    if site_id is None:
        site_id = settings.SITE_ID

    for lang_dict in FLUENT_BLOGS_LANGUAGES.get(site_id, ()):
        if lang_dict['code'] == language_code:
            return lang_dict

    return FLUENT_BLOGS_LANGUAGES['default']


# Perform version checks
if len(FLUENT_BLOGS_LANGUAGES.get(settings.SITE_ID, ())) > 1:
    import sys
    from distutils.version import StrictVersion, LooseVersion
    if sys.version_info[0] == 2 and sys.version_info[1] < 7:
        Version = LooseVersion  # 2.6 does not allow 1.0c1
    else:
        Version = StrictVersion

    import fluent_contents
    if Version(fluent_contents.__version__) < Version('1.0a1'):
        raise ImproperlyConfigured("Using the multilingual support requires django-fluent-contents 1.0")
