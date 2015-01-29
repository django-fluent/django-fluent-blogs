from datetime import date, datetime
from django.conf import settings
from django.template import Library
from fluent_blogs.models import get_entry_model
from fluent_blogs.models.query import query_entries, query_tags
from tag_parser import template_tag
from tag_parser.basetags import BaseAssignmentOrInclusionNode, BaseAssignmentOrOutputNode

BlogPage = None

HAS_APP_URLS = 'fluent_pages' in settings.INSTALLED_APPS
if HAS_APP_URLS:
    # HACK: accessing BlogPage directly. Apps are not completely separated this way.
    # Should have some kind of registry and filter system (like middleware) instead.
    from fluent_blogs.pagetypes.blogpage.models import BlogPage


register = Library()


@register.tag
def blogurl(parser, token):
    """
    Compatibility tag to allow django-fluent-blogs to operate stand-alone.
    Either the app can be hooked in the URLconf directly, or it can be added as a pagetype of django-fluent-pages.
    For the former, URL resolving works via the normal '{% url "viewname" arg1 arg2 %}' syntax.
    For the latter, the URL resolving works via '{% appurl "viewname" arg1 arg2 %}' syntax.
    """
    if HAS_APP_URLS:
        from fluent_pages.templatetags.appurl_tags import appurl
        return appurl(parser, token)
    else:
        # Using url from future, so the syntax is the same modern style.
        from django.templatetags.future import url
        return url(parser, token)


@template_tag(register, 'get_entry_url')
class GetEntryUrl(BaseAssignmentOrOutputNode):
    """
    Get the URL of a blog entry.

    When using django-fluent-pages, this takes the current ``page`` variable into account.
    It makes sure the blog entry is relative to the current page.

    When django-fluent-pages is not used, using this is identical to calling ``entry.get_absolute_url()``.
    """
    min_args = 1
    max_args = 1
    takes_context = True

    def get_value(self, context, *tag_args, **tag_kwargs):
        entry = tag_args[0]

        if HAS_APP_URLS:
            # If the application supports mounting a BlogPage in the page tree,
            # that can be used as relative start point of the entry.
            page = context.get('page')
            request = context.get('request')
            if page is None and request is not None:
                # HACK: access private django-fluent-pages var
                page = getattr(request, '_current_fluent_page', None)

            if page is not None and isinstance(page, BlogPage):
                return page.get_entry_url(entry)

        return entry.get_absolute_url()


@register.filter
def format_year(year):
    """
    Compatibility tag for Django 1.4.
    Format the year value of the ``YearArchiveView``,
    which can be a integer or date object.
    """
    if isinstance(year, (date, datetime)):
        # Django 1.5 and up, 'year' is a date object, consistent with month+day views.
        return unicode(year.year)
    else:
        # Django 1.4 just passes the kwarg as string.
        return unicode(year)


class BlogAssignmentOrInclusionNode(BaseAssignmentOrInclusionNode):
    """
    Internal class, to make sure additional context is passed to the inclusion-templates.
    """

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        context = super(BlogAssignmentOrInclusionNode, self).get_context_data(parent_context, *tag_args, **tag_kwargs)

        # Also pass 'request' and 'page' if they are available.
        # This helps the 'blogurl' and 'appurl' tags to resolve the current blog pagetype,
        # if there are multiple pagetypes available.
        for var in ('request', 'page'):
            value = parent_context.get(var)
            if value:
                context[var] = value

        return context


@template_tag(register, 'get_entries')
class GetEntriesNode(BlogAssignmentOrInclusionNode):
    """
    Query the entries in the database, and render them.
    This template tag supports the following syntax:

    .. code-block:: html+django

        {% get_entries category='slug' year=2012 as entries %}
        {% for entry in entries %}...{% endfor %}

        {% get_entries category='slug' year=2012 template="name/of/template.html" %}

    The allowed query parameters are:

    * ``category``: The slug or ID of a category
    * ``tag``: The slug or ID of a tag
    * ``author``: The username or ID of an author
    * ``year``: The full year.
    * ``month``: The month number to display
    * ``day``: The day of the month to display.
    * ``order``: Which field to order on, this can be:

     * ``slug``: The URL name of the entry.
     * ``title``: The title of the entry.
     * ``author``: The author full name
     * ``author_slug``: The author URL name.
     * ``category``: The category name.
     * ``category_slug``: The category URL name.
     * ``tag``: The tag name
     * ``tag_slug``: The tag URL name.
     * ``date``: The publication date of the entry.

    * ``orderby``: can be ASC/ascending or DESC/descending. The default depends on the ``order`` field.
    * ``limit``: The maximum number of entries to return.
    """
    template_name = "fluent_blogs/templatetags/entries.html"
    context_value_name = 'entries'
    allowed_kwargs = (
        'category', 'tag', 'author',
        'year', 'month', 'day',
        'orderby', 'order', 'limit',
    )
    model = get_entry_model()

    def get_value(self, context, *tag_args, **tag_kwargs):
        # Query happens in the backend,
        # the templatetag is considered to be a frontend.
        qs = self.model.objects.all()
        qs = query_entries(qs, **tag_kwargs)
        return qs


@template_tag(register, 'get_tags')
class GetPopularTagsNode(BlogAssignmentOrInclusionNode):
    """
    Find the popular tags associated with blog entries.
    This template tag supports the following syntax:

    .. code-block:: html+django

        {% get_tags order="name" as tags %}
        {% for tag in tags %}...{% endfor %}

        {% get_tags template="name/of/template.html" %}

    The allowed query parameters are:

    * ``order``: Which field to order on, this can be:

     * ``slug``: The URL name of the tag.
     * ``name``: The name of the tag.
     * ``count``: The number of times the tag is used.

    * ``orderby``: can be ASC/ascending or DESC/descending. The default depends on the ``order`` field.
    * ``limit``: The maximum number of entries to return.

    The returned :class:`~taggit.models.Tag` objects have a ``count`` attribute attached
    with the amount of times the tag is used.
    """
    template_name = "fluent_blogs/templatetags/popular_tags.html"
    context_value_name = 'tags'
    allowed_kwargs = (
        'order', 'orderby', 'limit',
    )

    def get_value(self, context, *tag_args, **tag_kwargs):
        return query_tags(**tag_kwargs)


if False and __debug__:
    # This only exists to make PyCharm happy:
    # The real syntax should be passing the ``.parse`` method to the function.
    register.tag('get_entries', GetEntriesNode)
    register.tag('get_entry_url', GetEntryUrl)
    register.tag('get_tags', GetPopularTagsNode)
