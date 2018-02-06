from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import feedgenerator
from django.utils.encoding import force_text
from django.utils.translation import gettext
from django.views.generic import View
from fluent_blogs import appsettings
from fluent_blogs.models import get_entry_model
from fluent_blogs.models.query import get_category_for_slug
from fluent_blogs.urlresolvers import blog_reverse

_FEED_FORMATS = {
    'atom1': feedgenerator.Atom1Feed,
    'rss0.91': feedgenerator.RssUserland091Feed,
    'rss2.0': feedgenerator.Rss201rev2Feed,
}

__all__ = (
    'LatestEntriesFeed', 'LatestCategoryEntriesFeed', 'LatestAuthorEntriesFeed', 'LatestTagEntriesFeed'
)


def get_entry_queryset():
    # Avoid being cached at module level, always return a new queryset.
    return get_entry_model().objects.published().active_translations().order_by('-publication_date')


_max_items = appsettings.FLUENT_BLOGS_MAX_FEED_ITEMS


class FeedView(View, Feed):
    """
    Bridge to let Django syndication feeds operate like a normal class-based-view.
    This introduces the ``as_view()`` method, attributes like ``self.request`` and allows to assign attributes to 'self'.
    """
    format = 'rss2.0'

    def __init__(self, **kwargs):
        View.__init__(self, **kwargs)

        # Allow this view to easily switch between feed formats.
        format = kwargs.get('format', self.format)
        try:
            self.feed_type = _FEED_FORMATS[format]
        except KeyError:
            raise ValueError("Unsupported feed format: {0}. Supported are: {1}".format(
                self.format, ', '.join(sorted(_FEED_FORMATS.keys()))
            ))

    def get(self, request, *args, **kwargs):
        # Pass flow to the original Feed.__call__
        return self.__call__(request, *args, **kwargs)


class EntryFeedBase(FeedView):
    """
    Base class for all feeds returning blog entries.
    """

    def items(self, object=None):
        return get_entry_queryset()[:_max_items]

    def reverse(self, viewname, args=None, kwargs=None):
        """
        Reverse a blog page, taking different configuration options into account.
        For example, the blog can be mounted using *django-fluent-pages* on multiple nodes.
        """
        # TODO: django-fluent-pages needs a public API to get the current page.
        current_page = getattr(self.request, '_current_fluent_page', None)
        return blog_reverse(viewname, args=args, kwargs=kwargs, current_page=current_page)

    # -- general

    def item_title(self, entry):
        return entry.title

    @property
    def description_template(self):
        EntryModel = get_entry_model()
        templates = [
            "{0}/{1}_feed_description.html".format(EntryModel._meta.app_label, EntryModel._meta.object_name.lower()),
            "fluent_blogs/entry_feed_description.html",  # New name
            "fluent_blogs/feeds/entry/description.html"  # Old name
        ]
        # The value is passed to get_template by the Feed class, so reduce the list here manually.
        for name in templates:
            try:
                get_template(name)
            except TemplateDoesNotExist:
                pass
            else:
                setattr(self.__class__, 'description_template', name)
                return templates
        return None

    def item_pubdate(self, entry):
        return entry.publication_date

    def item_guid(self, entry):
        return entry.get_short_url()  # Have something consistent!

    # item_enclosure_url
    # item_enclosure_length
    # item_enclosure_mime_type
    # item_copyright

    # -- sub objects

    def item_author_name(self, entry):
        return entry.author.get_full_name() if entry.author else None

    def item_author_email(self, entry):
        return entry.author.email if entry.author else None

    def item_author_link(self, entry):
        return self.reverse('entry_archive_author', kwargs={'slug': entry.author.get_username()}) if entry.author else None

    def item_categories(self, entry):
        return [force_text(category) for category in entry.categories.all()]


class LatestEntriesFeed(EntryFeedBase):
    """
    Feed for the latest entries of the blog.
    """

    def get_object(self, request, *args, **kwargs):
        return get_current_site(request)

    def title(self, site):
        return gettext(u"{site_name} - Latest entries").format(site_name=site.name)

    def subtitle(self, site):
        return self.description(site)  # For Atom1 feeds

    def description(self, site):
        return gettext(u"The latest entries for {site_name}").format(site_name=site.name)

    def link(self, site):
        return self.reverse('entry_archive_index')


class LatestCategoryEntriesFeed(EntryFeedBase):
    """
    Feed for the latest entries in a category.
    """

    def get_object(self, request, slug):
        return get_category_for_slug(slug)

    def items(self, category):
        return get_entry_queryset().filter(categories=category)[:_max_items]

    def title(self, category):
        # django-categories uses 'name', django-categories-i18n uses 'title'
        category_name = force_text(category)
        return gettext(u"Entries in the category {category_name}").format(category_name=category_name)

    def subtitle(self, category):
        return self.description(category)  # For Atom1 feeds

    def description(self, category):
        category_name = force_text(category)
        return gettext(u"The latest entries in the category {category_name}").format(category_name=category_name)

    def link(self, category):
        return self.reverse('entry_archive_category', kwargs={'slug': category.slug})


class LatestAuthorEntriesFeed(EntryFeedBase):
    """
    Feed for the latest entries with a author.
    """

    def get_object(self, request, slug):
        User = get_user_model()
        return get_object_or_404(User, **{User.USERNAME_FIELD: slug})

    def items(self, author):
        return get_entry_queryset().filter(author=author)[:_max_items]

    def title(self, author):
        return gettext(u"Entries by {author_name}").format(author_name=author.get_full_name())

    def subtitle(self, author):
        return self.description(author)  # For Atom1 feeds

    def description(self, author):
        return gettext(u"The latest entries written by {author_name}").format(author_name=author.get_full_name())

    def link(self, author):
        return self.reverse('entry_archive_author', kwargs={'slug': author.get_username()})


class LatestTagEntriesFeed(EntryFeedBase):
    """
    Feed for the latest entries with a tag.
    """

    def get_object(self, request, slug):
        from taggit.models import Tag  # Taggit is still an optional dependency
        return get_object_or_404(Tag, slug=slug)

    def items(self, tag):
        return get_entry_queryset().filter(tags=tag)[:_max_items]

    def title(self, tag):
        return gettext(u"Entries for the tag {tag_name}").format(tag_name=tag.name)

    def subtitle(self, tag):
        return self.description(tag)  # For Atom1 feeds

    def description(self, tag):
        return gettext(u"The latest entries tagged with {tag_name}").format(tag_name=tag.name)

    def link(self, tag):
        return self.reverse('entry_archive_tag', kwargs={'slug': tag.slug})
