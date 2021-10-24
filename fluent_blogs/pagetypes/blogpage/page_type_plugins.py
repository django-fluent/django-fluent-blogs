from fluent_pages.extensions import PageTypePlugin, page_type_pool

from fluent_blogs.pagetypes.blogpage.models import BlogPage

from .admin import BlogPageAdmin


@page_type_pool.register
class BlogPagePlugin(PageTypePlugin):
    model = BlogPage
    model_admin = BlogPageAdmin
    urls = "fluent_blogs.urls"
