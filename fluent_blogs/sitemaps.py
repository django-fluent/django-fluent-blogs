from categories.models import Category
from django.contrib.sitemaps import Sitemap
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
        only_ids = Entry.objects.values('categories').order_by().distinct()
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
        only_ids = Entry.objects.values('author').order_by().distinct()
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
        from taggit.models import TaggedItem, Tag
        only_ids = TaggedItem.tags_for(Entry).values('id').order_by().distinct()
        return Tag.objects.filter(taggit_taggeditem_items__in=only_ids)

    def lastmod(self, tag):
        """Return the last modification of the entry."""
        lastitems = Entry.objects.published().order_by('-modification_date').filter(tags=tag).only('modification_date')
        return lastitems[0].modification_date

    def location(self, tag):
        """Return url of an entry."""
        return blog_reverse('entry_archive_tag', kwargs={'slug': tag.slug}, ignore_multiple=True)
