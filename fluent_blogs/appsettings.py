from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from parler import appsettings as parler_appsettings
from parler.utils import is_supported_django_language, normalize_language_code

if 'categories' in settings.INSTALLED_APPS:
    # old django-categories style. Keep first for backwards compatibility
    _default_category_model = 'categories.Category'
elif 'categories_i18n' in settings.INSTALLED_APPS:
    _default_category_model = 'categories_i18n.Category'
else:
    # Default to new.
    _default_category_model = 'categories_i18n.Category'


# Configurable permalink style, yeah!
FLUENT_BLOGS_ENTRY_LINK_STYLE = getattr(settings, "FLUENT_BLOGS_ENTRY_LINK_STYLE", '/{year}/{month}/{slug}/')

# Configurable admin fields
# By default, all optional mixin fields are detected.
FLUENT_BLOGS_EXTRA_ADMIN_FIELDS = getattr(settings, 'FLUENT_BLOGS_EXTRA_ADMIN_FIELDS', ())
FLUENT_BLOGS_ADMIN_FIELDS = getattr(settings, 'FLUENT_BLOGS_ADMIN_FIELDS', tuple(FLUENT_BLOGS_EXTRA_ADMIN_FIELDS) + ('excerpt_image', 'excerpt_text', 'contents', 'categories', 'tags', 'enable_comments'))

# Advanced settings
FLUENT_BLOGS_FILTER_SITE_ID = getattr(settings, 'FLUENT_BLOGS_FILTER_SITE_ID', True)
FLUENT_BLOGS_BASE_TEMPLATE = getattr(settings, "FLUENT_BLOGS_BASE_TEMPLATE", 'fluent_blogs/base.html')
FLUENT_BLOGS_CATEGORY_MODEL = getattr(settings, "FLUENT_BLOGS_CATEGORY_MODEL", _default_category_model)
FLUENT_BLOGS_ENTRY_MODEL = getattr(settings, "FLUENT_BLOGS_ENTRY_MODEL", 'fluent_blogs.Entry')

# RSS feeds
FLUENT_BLOGS_FEED_PROTOCOL = getattr(settings, "FLUENT_BLOGS_FEED_PROTOCOL", 'http')
FLUENT_BLOGS_MAX_FEED_ITEMS = getattr(settings, "FLUENT_BLOGS_MAX_FEED_ITEMS", 30)

# Comment settings
FLUENT_BLOGS_INCLUDE_STATIC_FILES = getattr(settings, "FLUENT_BLOGS_INCLUDE_STATIC_FILES", True)
FLUENT_BLOGS_PAGINATE_BY = getattr(settings, "FLUENT_BLOGS_PAGINATE_BY", 10)

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
        site_id = getattr(settings, 'SITE_ID', None)

    for lang_dict in FLUENT_BLOGS_LANGUAGES.get(site_id, ()):
        if lang_dict['code'] == language_code:
            return lang_dict

    return FLUENT_BLOGS_LANGUAGES['default']
