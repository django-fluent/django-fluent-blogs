from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import Sitemap
from django.db.models import get_model
from fluent_blogs import appsettings
from fluent_blogs.models import Entry
from fluent_blogs.urlresolvers import blog_reverse
from fluent_blogs.utils.compat import get_user_model


class EntrySitemap(Sitemap):
    """
    The sitemap definition for the pages created with django-fluent-pages.
    """
    def items(self):
        return Entry.objects.published().order_by('slug')

    def lastmod(self, urlnode):
        """Return the last modification of the entry."""
        return urlnode.modification_date

    def location(self, urlnode):
        """Return url of an entry."""
        return urlnode.url


class CategoryArchiveSitemap(Sitemap):
    def items(self):
        only_ids = Entry.objects.published().values('categories').order_by().distinct()
        Category = get_model(appsettings.FLUENT_BLOGS_CATEGORY_MODEL)
        return Category.objects.filter(id__in=only_ids)

    def lastmod(self, category):
        """Return the last modification of the entry."""
        lastitems = Entry.objects.published().order_by('-modification_date').filter(categories=category).only('modification_date')
        return lastitems[0].modification_date

    def location(self, category):
        """Return url of an entry."""
        return blog_reverse('entry_archive_category', kwargs={'slug': category.slug}, ignore_multiple=True)


class AuthorArchiveSitemap(Sitemap):
    def items(self):
        User = get_user_model()
        only_ids = Entry.objects.published().values('author').order_by().distinct()
        return User.objects.filter(id__in=only_ids)

    def lastmod(self, author):
        """Return the last modification of the entry."""
        lastitems = Entry.objects.published().order_by('-modification_date').filter(author=author).only('modification_date')
        return lastitems[0].modification_date

    def location(self, author):
        """Return url of an entry."""
        return blog_reverse('entry_archive_author', kwargs={'slug': author.username}, ignore_multiple=True)


class TagArchiveSitemap(Sitemap):
    def items(self):
        # Tagging is optional. When it's not used, it's ignored.
        if 'taggit' not in settings.INSTALLED_APPS:
            return []

        from taggit.models import Tag
        only_instances = Entry.objects.published().only('pk')

        # Until https://github.com/alex/django-taggit/pull/86 is merged,
        # better use the field names directly instead of bulk_lookup_kwargs
        return Tag.objects.filter(
            taggit_taggeditem_items__object_id__in=only_instances,
            taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(Entry)
        )

    def lastmod(self, tag):
        """Return the last modification of the entry."""
        lastitems = Entry.objects.published().order_by('-modification_date').filter(tags=tag).only('modification_date')
        return lastitems[0].modification_date

    def location(self, tag):
        """Return url of an entry."""
        return blog_reverse('entry_archive_tag', kwargs={'slug': tag.slug}, ignore_multiple=True)
