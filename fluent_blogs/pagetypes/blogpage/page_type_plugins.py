from fluent_blogs.pagetypes.blogpage.models import BlogPage
from fluent_pages.extensions import page_type_pool, PageTypePlugin
from .admin import BlogPageAdmin


@page_type_pool.register
class BlogPagePlugin(PageTypePlugin):
    model = BlogPage
    model_admin = BlogPageAdmin
    urls = 'fluent_blogs.urls'
