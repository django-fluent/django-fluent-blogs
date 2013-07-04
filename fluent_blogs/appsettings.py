from django.conf import settings

# Configurable permalink style, yeah!
FLUENT_BLOGS_ENTRY_LINK_STYLE = getattr(settings, "FLUENT_BLOGS_ENTRY_LINK_STYLE", '/{year}/{month}/{slug}/')
FLUENT_BLOGS_BASE_TEMPLATE = getattr(settings, "FLUENT_BLOGS_BASE_TEMPLATE", 'fluent_blogs/base.html')
FLUENT_BLOGS_CATEGORY_MODEL = getattr(settings, "FLUENT_BLOGS_CATEGORY_MODEL", 'categories.Category')
FLUENT_BLOGS_ENTRY_MODEL = getattr(settings, "FLUENT_BLOGS_ENTRY_MODEL", 'fluent_blogs.Entry')

FLUENT_BLOGS_FEED_PROTOCOL = getattr(settings, "FLUENT_BLOGS_FEED_PROTOCOL", 'http')
FLUENT_BLOGS_MAX_FEED_ITEMS = getattr(settings, "FLUENT_BLOGS_MAX_FEED_ITEMS", 30)

FLUENT_BLOGS_INCLUDE_STATIC_FILES = getattr(settings, "FLUENT_BLOGS_INCLUDE_STATIC_FILES", True)
