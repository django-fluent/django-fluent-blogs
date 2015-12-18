from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import Sitemap
from fluent_blogs.models import get_entry_model, get_category_model
from fluent_blogs.urlresolvers import blog_reverse
from fluent_utils.django_compat import get_user_model
from parler.models import TranslatableModel

User = get_user_model()
EntryModel = get_entry_model()
CategoryModel = get_category_model()


class EntrySitemap(Sitemap):
    """
    The sitemap definition for the pages created with django-fluent-blogs.
    """

    def items(self):
        qs = EntryModel.objects.published().order_by('-publication_date')

        if issubclass(EntryModel, TranslatableModel):
            # Note that .active_translations() can't be combined with other filters for translations__.. fields.
            qs = qs.active_translations()
            return qs.order_by('-publication_date', 'translations__language_code')
        else:
            return qs.order_by('-publication_date')

    def lastmod(self, urlnode):
        """Return the last modification of the entry."""
        return urlnode.modification_date

    def location(self, urlnode):
        """Return url of an entry."""
        return urlnode.url


class CategoryArchiveSitemap(Sitemap):

    def items(self):
        only_ids = EntryModel.objects.published().values('categories').order_by().distinct()
        return CategoryModel.objects.filter(id__in=only_ids)

    def lastmod(self, category):
        """Return the last modification of the entry."""
        lastitems = EntryModel.objects.published().order_by('-modification_date').filter(categories=category).only('modification_date')
        return lastitems[0].modification_date

    def location(self, category):
        """Return url of an entry."""
        return blog_reverse('entry_archive_category', kwargs={'slug': category.slug}, ignore_multiple=True)


class AuthorArchiveSitemap(Sitemap):

    def items(self):
        only_ids = EntryModel.objects.published().values('author').order_by().distinct()
        return User.objects.filter(id__in=only_ids)

    def lastmod(self, author):
        """Return the last modification of the entry."""
        lastitems = EntryModel.objects.published().order_by('-modification_date').filter(author=author).only('modification_date')
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
        only_instances = EntryModel.objects.published().only('pk')

        # Until https://github.com/alex/django-taggit/pull/86 is merged,
        # better use the field names directly instead of bulk_lookup_kwargs
        return Tag.objects.filter(
            taggit_taggeditem_items__object_id__in=only_instances,
            taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(EntryModel)
        )

    def lastmod(self, tag):
        """Return the last modification of the entry."""
        lastitems = EntryModel.objects.published().order_by('-modification_date').filter(tags=tag).only('modification_date')
        return lastitems[0].modification_date

    def location(self, tag):
        """Return url of an entry."""
        return blog_reverse('entry_archive_tag', kwargs={'slug': tag.slug}, ignore_multiple=True)
