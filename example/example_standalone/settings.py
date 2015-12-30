# Django settings for example project.
from os.path import join, dirname, realpath
import django

# Add parent path,
# Allow starting the app without installing the module.
import sys
sys.path.insert(0, dirname(dirname(dirname(realpath(__file__)))))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': dirname(dirname(__file__)) + '/demo.db',
    }
}

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'en'   # Important when switching to multilingual support!
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = join(dirname(__file__), "media")
MEDIA_URL = '/media/'
STATIC_ROOT = join(dirname(__file__), "static")
STATIC_URL = '/static/'

STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-#@bi6bue%#1j)6+4b&#i0g-*xro@%f@_#zwv=2-g_@n3n_kj5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

ROOT_URLCONF = 'example_standalone.urls'

TEMPLATE_DIRS = (
    join(dirname(__file__), "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Site theme.
    # Placed above all other apps, to override third party apps
    'theme1',

    # Blog module
    'fluent_blogs',

    # Contents plugins
    'fluent_contents',
    'fluent_contents.plugins.code',
    'fluent_contents.plugins.commentsarea',
    #'fluent_contents.plugins.disquswidgets',
    #'fluent_contents.plugins.formdesignerlink',
    'fluent_contents.plugins.gist',
    'fluent_contents.plugins.googledocsviewer',
    'fluent_contents.plugins.iframe',
    'fluent_contents.plugins.markup',
    'fluent_contents.plugins.oembeditem',
    'fluent_contents.plugins.rawhtml',
    #'fluent_contents.plugins.sharedcontent',
    'fluent_contents.plugins.text',
    #'fluent_contents.plugins.twitterfeed',

    # Other (optional) dependencies
    'categories',                    # default 'categories' app, can be changed.
    'categories.editor',
    'django.contrib.comments',       # should be below theme1
    'django_wysiwyg',                # for 'text' plugin
    #'disqus',                       # for 'disqus' plugin
    #'form_designer',                # for 'formdesignerlink' plugin
    'parler',                        # provides the multilingual support.
    'slug_preview',                  # nicer slugs in the admin.
    'taggit',                        # optional tagging support.
    'taggit_autosuggest',            # optional autocompletion support for tags
    'tinymce',                       # Used by 'text' plugin, see DJANGO_WYSIWYG_FLAVOR
)

if django.VERSION < (1, 7):
    INSTALLED_APPS += (
        # For DB upgrades
        'south',
    )
else:
    TEST_RUNNER = 'django.test.runner.DiscoverRunner'  # silence system checks

DJANGO_WYSIWYG_FLAVOR = 'tinymce_advanced'

# Being explicit for now
FLUENT_BLOGS_BASE_TEMPLATE = 'fluent_blogs/base.html'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#DISQUS_API_KEY = ''
#DISQUS_WEBSITE_SHORTNAME = ''
