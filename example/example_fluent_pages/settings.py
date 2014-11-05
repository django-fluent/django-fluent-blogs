from os.path import join, dirname
from example_standalone.settings import *

INSTALLED_APPS += (
    # Add fluent pages with a simple page type:
    'fluent_pages',
    #'fluent_pages.pagetypes.fluentpage',
    'fluent_pages.pagetypes.flatpage',

    # Add the page type for adding the "blogs" root to the page tree.
    'fluent_blogs.pagetypes.blogpage',

    # fluent-pages dependencies:
    'mptt',
    'polymorphic',
    'polymorphic_tree',
)

ROOT_URLCONF = 'example_fluent_pages.urls'

TEMPLATE_DIRS = (
    join(dirname(__file__), "templates"),
)
