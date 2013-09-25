from example_standalone.settings import *

INSTALLED_APPS = (
    'fluent_comments',
    'crispy_forms',
) + INSTALLED_APPS

COMMENTS_APP = 'fluent_comments'

ROOT_URLCONF = 'example_fluent_comments.urls'

#AKISMET_API_KEY = ''

# Being explicit here, auto includes comment-static files:
FLUENT_BLOGS_INCLUDE_STATIC_FILES = True
