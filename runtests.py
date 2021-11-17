#!/usr/bin/env python -Wd
import sys
import warnings
from os import path

import django
from django.conf import global_settings as default_settings
from django.conf import settings
from django.core.management import execute_from_command_line

# python -Wd, or run via coverage:
warnings.simplefilter("always", DeprecationWarning)

# Give feedback on used versions
sys.stderr.write(f"Using Python version {sys.version[:5]} from {sys.executable}\n")
sys.stderr.write(
    "Using Django version {} from {}\n".format(
        django.get_version(), path.dirname(path.abspath(django.__file__))
    )
)

if not settings.configured:
    import fluent_pages

    pages_root = path.dirname(path.abspath(fluent_pages.__file__))

    settings.configure(
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        },
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "django.contrib.admin",
            "django.contrib.sessions",
            "django.contrib.messages",
            "fluent_pages",
            "fluent_blogs",
            "fluent_blogs.pagetypes.blogpage",
            "fluent_contents",
            "categories_i18n",
            "django_wysiwyg",
            "mptt",
            "parler",
            "polymorphic",
            "polymorphic_tree",
        ),
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ),
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": (),
                "OPTIONS": {
                    "loaders": (
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ),
                    "context_processors": (
                        "django.template.context_processors.debug",
                        "django.template.context_processors.i18n",
                        "django.template.context_processors.media",
                        "django.template.context_processors.request",
                        "django.template.context_processors.static",
                        "django.contrib.messages.context_processors.messages",
                        "django.contrib.auth.context_processors.auth",
                    ),
                },
            },
        ],
        ROOT_URLCONF="fluent_blogs.tests.testapp.urls",
        TEST_RUNNER="django.test.runner.DiscoverRunner",
        SECRET_KEY="testtest",
        SITE_ID=4,
        PARLER_LANGUAGES={
            4: (
                {"code": "nl", "fallback": "en"},
                {"code": "en"},
            ),
        },
        PARLER_DEFAULT_LANGUAGE_CODE="en",  # Having a good fallback causes more code to run, more error checking.
        FLUENT_PAGES_TEMPLATE_DIR=path.join(pages_root, "tests", "testapp", "templates"),
        FLUENT_BLOGS_ENTRY_MODEL="fluent_blogs.Entry",  # for explicit testing
    )

DEFAULT_TEST_APPS = [
    "fluent_blogs",
]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith("-"), sys.argv[1:]))
    test_apps = (
        list(filter(lambda arg: not arg.startswith("-"), sys.argv[1:])) or DEFAULT_TEST_APPS
    )
    argv = sys.argv[:1] + ["test", "--traceback"] + other_args + test_apps
    execute_from_command_line(argv)


if __name__ == "__main__":
    runtests()
