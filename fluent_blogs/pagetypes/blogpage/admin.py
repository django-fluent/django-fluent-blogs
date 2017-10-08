from django.contrib import admin
from fluent_pages.integration.fluent_contents.admin import FluentContentsPageAdmin
from .models import BlogPage


@admin.register(BlogPage)
class BlogPageAdmin(FluentContentsPageAdmin):
    """
    Customized admin appearance for the blogpage model.
    """
    placeholder_layout_template = "fluent_blogs/entry_archive_index.html"
