from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from athumb.fields import ImageWithThumbsField
from parler.fields import TranslatedField
from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.utils.context import switch_language

from fluent_blogs.urlresolvers import blog_reverse
from fluent_blogs.models.managers import EntryManager, TranslatableEntryManager
from fluent_blogs import appsettings
from fluent_contents.models import PlaceholderField, ContentItemRelation, Placeholder
from fluent_utils.django_compat import AUTH_USER_MODEL
from fluent_utils.softdeps.comments import CommentsMixin
from fluent_utils.softdeps.taggit import TagsMixin

# Rename to old class names
CommentsEntryMixin = CommentsMixin

__all__ = (
    # Mixins
    'AbstractSharedEntryBaseMixin',
    'AbstractTranslatedFieldsEntryBaseMixin',
    'ExcerptEntryMixin',
    'ContentsEntryMixin',
    'CommentsEntryMixin',
    'CategoriesEntryMixin',
    'TagsEntryMixin',
    'SeoEntryMixin',

    # Untranslated base classes
    'AbstractEntryBase',
    'AbstractEntry',

    # Translated base classes.
    'AbstractTranslatableEntryBase',
    'AbstractTranslatableEntry',
    'AbstractTranslatedFieldsEntryBase',
    'AbstractTranslatedFieldsEntry',
)

def _get_current_site():
    return Site.objects.get_current().pk


class AbstractTranslatedFieldsEntryBaseMixin(models.Model):
    """
    The base translated fields.
    """
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"))

    class Meta:
        abstract = True


class AbstractSharedEntryBaseMixin(models.Model):
    """
    The basic interface for blog entries.
    """
    #: Tagging marker for code to recognize translated models.
    is_translatable_model = False

    # Some publication states
    DRAFT = 'd'
    PUBLISHED = 'p'
    STATUSES = (
        (PUBLISHED, _('Published')),
        (DRAFT, _('Draft')),
    )

    parent_site = models.ForeignKey(Site, editable=False, default=_get_current_site)

    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_('''When the entry should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)

    # Metadata
    author = models.ForeignKey(AUTH_USER_MODEL, verbose_name=_('author'))
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    # Image with thumbnail
    image = ImageWithThumbsField(
        upload_to="blog_images",
        thumbs=(
            ('50x50_cropped', {'size': (50, 50), 'crop': True}),
            ('60x60', {'size': (60, 60)}),
            ('100x100', {'size': (100, 100)}),
            ('front_page', {'size': (300, 300)}),
            ('medium', {'size': (600, 600)}),
            ('large', {'size': (1000, 1000)}),
        ),
        blank=True, null=True,
    )

    objects = EntryManager()

    class Meta:
        verbose_name = _("Blog entry")
        verbose_name_plural = _("Blog entries")
        ordering = ('-publication_date',)
        get_latest_by = "publication_date"  # Support Entry.objects.latest() call.
        abstract = True


    def __unicode__(self):
        return self.title


    def get_absolute_url(self):
        return self.default_url


    @property
    def default_url(self):
        """
        The internal implementation of :func:`get_absolute_url`.
        This function can be used when overriding :func:`get_absolute_url` in the settings.
        For example::

            ABSOLUTE_URL_OVERRIDES = {
                'fluent_blogs.Entry': lambda o: "http://example.com" + o.default_url
            }
        """
        root = blog_reverse('entry_archive_index', ignore_multiple=True, language_code=self.get_current_language())
        return root + self.get_relative_url()


    def get_relative_url(self):
        """
        Return the link path from the archive page.
        """
        # Return the link style, using the permalink style setting.
        return appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE.lstrip('/').format(
            year = self.publication_date.strftime('%Y'),
            month = self.publication_date.strftime('%m'),
            day = self.publication_date.strftime('%d'),
            slug = self.slug,
            pk = self.pk,
        )


    def get_current_language(self):
        return None  # Normal untranslated model: the API is there, but unused.


    def get_short_url(self):
        return blog_reverse('entry_shortlink', kwargs={'pk': self.pk}, ignore_multiple=True)


    @property
    def url(self):
        """
        The URL of the entry, provided for template code.
        """
        return self.get_absolute_url()


    @property
    def is_published(self):
        return self.status == self.PUBLISHED


    @property
    def is_draft(self):
        return self.status == self.DRAFT


    @property
    def previous_entry(self):
        """
        Return the previous entry
        """
        if not self.publication_date:
            # Protection for manually created models (Entry.objects.create())
            return None
        qs = self.__class__.objects.published()
        if self.is_translatable_model:
            qs = qs.translated()

        entries = qs.filter(publication_date__lt=self.publication_date).order_by('-publication_date')[:1]
        return entries[0] if entries else None


    @property
    def next_entry(self):
        """
        Return the next entry
        """
        if not self.publication_date:
            return None
        qs = self.__class__.objects.published()
        if self.is_translatable_model:
            qs = qs.translated()

        entries = qs.filter(publication_date__gt=self.publication_date).order_by('publication_date')[:1]
        return entries[0] if entries else None


class ExcerptEntryMixin(models.Model):
    """
    Mixin for adding the excerpt text to a blog entry.
    """
    intro = models.TextField(_("Introtext"))

    class Meta:
        abstract = True


class ContentsEntryMixin(models.Model):
    """
    Mixin for adding contents to a blog entry
    """
    contents = PlaceholderField("blog_contents")

    # Adding the ContentItemRelation makes sure the admin can find all deleted objects too.
    contentitem_set = ContentItemRelation()

    class Meta:
        abstract = True

    def create_placeholder(self, slot="blog_contents", role='m', title=None):
        """
        Create a placeholder on this blog entry.

        To fill the content items, use
        :func:`ContentItemModel.objects.create_for_placeholder() <fluent_contents.models.managers.ContentItemManager.create_for_placeholder>`.

        :rtype: :class:`~fluent_contents.models.Placeholder`
        """
        return Placeholder.objects.create_for_object(self, slot, role=role, title=title)


class CategoriesEntryMixin(models.Model):
    """
    Mixin for adding category support to a blog entry.
    """
    categories = models.ManyToManyField(appsettings.FLUENT_BLOGS_CATEGORY_MODEL, verbose_name=_("Categories"), blank=True)

    class Meta:
        abstract = True


class TagsEntryMixin(TagsMixin):
    """
    Mixin for adding tags to a blog entry
    """
    class Meta:
        abstract = True

    def similar_objects(self, num=None, **filters):
        """
        Find similar objects using related tags.
        """
        #TODO: filter appsettings.FLUENT_BLOGS_FILTER_SITE_ID:
        #    filters.setdefault('parent_site', self.parent_site_id)

        # FIXME: Using super() doesn't work, calling directly.
        return TagsMixin.similar_objects(self, num=num, **filters)


class SeoEntryMixin(models.Model):
    """
    Mixin for adding SEO fields to a blog entry.
    """
    meta_keywords = models.CharField(_('keywords'), max_length=255, blank=True, default='', help_text=_("When this field is not filled in, the the tags will be used."))
    meta_description = models.CharField(_('description'), max_length=255, blank=True, default='', help_text=_("When this field is not filled in, the contents or intro text will be used."))
    meta_title = models.CharField(_('page title'), max_length=255, blank=True, null=True, help_text=_("When this field is not filled in, the menu title text will be used."))

    class Meta:
        abstract = True


class AbstractTranslatableEntryBase(
    TranslatableModel,
    AbstractSharedEntryBaseMixin):
    """
    The translatable abstract entry base model.
    """
    # Update tagging marker
    is_translatable_model = True

    title = TranslatedField(any_language=True)
    slug = TranslatedField()

    # Correct ordering of base classes should avoid getting the TranslatableModel.manager
    # to override the base classes. However, this caused other errors (django-parler not receiving abstract=True),
    # so kept the ordering in human-logical form, and restore the manager here.
    objects = TranslatableEntryManager()

    class Meta:
        abstract = True

    @property
    def default_url(self):
        """
        Make sure that the URL is translated in the current language.
        """
        with switch_language(self):
            return super(AbstractTranslatableEntryBase, self).default_url


class AbstractTranslatedFieldsEntryBase(
    TranslatedFieldsModel,
    AbstractTranslatedFieldsEntryBaseMixin):
    """
    The translatable fields for the base entry model.
    """
    master = None   # FK to shared model.

    class Meta:
        abstract = True


# For compatibility with old untranslated models.
class AbstractEntryBase(
    AbstractSharedEntryBaseMixin,
    AbstractTranslatedFieldsEntryBaseMixin):
    """
    The classic abstract entry base model.
    """
    # Not needed, but be explicit about the manager with this many base classes
    objects = EntryManager()

    class Meta:
        abstract = True


class AbstractEntry(
        AbstractEntryBase,
        ExcerptEntryMixin,
        ContentsEntryMixin,
        CommentsEntryMixin,
        CategoriesEntryMixin,
        TagsEntryMixin,
        SeoEntryMixin):
    """
    The classic entry model, as abstract model.
    """
    class Meta:
        abstract = True


class AbstractTranslatableEntry(
    AbstractTranslatableEntryBase,
    ContentsEntryMixin,
    CommentsEntryMixin,
    CategoriesEntryMixin,
    TagsEntryMixin):
    """
    The default entry model for translated blog posts, as abstract model.
    """
    class Meta:
        abstract = True


class AbstractTranslatedFieldsEntry(
    AbstractTranslatedFieldsEntryBase,
    ExcerptEntryMixin,
    SeoEntryMixin):
    """
    The default translated fields model for blog posts, as abstract model.
    """
    class Meta:
        abstract = True
