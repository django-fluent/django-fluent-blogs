from fluent_pages.integration.fluent_contents.admin import FluentContentsPageAdmin


class BlogPageAdmin(FluentContentsPageAdmin):
    """
    Customized admin appearance for the blogpage model.
    """
    placeholder_layout_template = "fluent_blogs/entry_archive_index.html"
