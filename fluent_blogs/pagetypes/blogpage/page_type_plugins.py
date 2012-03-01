from fluent_blogs.pagetypes.blogpage.models import BlogPage
from fluent_pages.extensions import page_type_pool, PageTypePlugin


@page_type_pool.register
class BlogPagePlugin(PageTypePlugin):
    model = BlogPage
    urls = 'fluent_blogs.urls'
