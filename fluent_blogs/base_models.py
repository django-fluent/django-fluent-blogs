from django.conf import settings
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.fields import TranslatedField
from parler.models import TranslatableModel, TranslatedFieldsModel
from fluent_blogs.urlresolvers import blog_reverse
from fluent_blogs.models.managers import EntryManager, TranslatableEntryManager
from fluent_blogs.utils.compat import get_user_model_name
from fluent_blogs import appsettings
from fluent_contents.models import PlaceholderField, ContentItemRelation
from parler.utils.context import switch_language

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


# Optional tagging support
TaggableManager = None
if 'taggit_autosuggest' in settings.INSTALLED_APPS:
    from taggit_autosuggest.managers import TaggableManager
elif 'taggit_autocomplete_modified' in settings.INSTALLED_APPS:
    from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
elif 'taggit' in settings.INSTALLED_APPS:
    from taggit.managers import TaggableManager


# Optional commenting support
# Make sure that django.contrib.comments is not imported in the app,
# unless it exists in INSTALLED_APPS. Otherwise, the User delete view
# breaks because it tries to delete comments associated with the user.
comments = None
moderator = None
CommentModel = None
CommentModerator = None
if 'django.contrib.comments' in settings.INSTALLED_APPS:
    from django.contrib import comments
    from django.contrib.comments.moderation import moderator, CommentModerator
    CommentModel = comments.get_model()

# Can't use EmptyQueryset stub in Django 1.6 anymore,
# using this model to build a queryset instead.
class CommentModelStub(models.Model):
    class Meta:
        managed = False
        db_table = "django_comments_stub"



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

    parent_site = models.ForeignKey(Site, editable=False, default=Site.objects.get_current)

    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_('''When the entry should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)

    # Metadata
    author = models.ForeignKey(get_user_model_name(), verbose_name=_('author'))
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

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


class CommentsEntryMixin(models.Model):
    """
    Mixin for adding comments support to a blog entry.
    """
    enable_comments = models.BooleanField(_("Enable comments"), default=True)


    # Make association with django.contrib.comments optional
    if CommentModel is not None:
        all_comments = GenericRelation(CommentModel, verbose_name=_("Comments"), object_id_field='object_pk')
    else:
        # Provide a stub so templates don't break.
        # This avoids importing django.contrib.comments models when the app is not used.
        all_comments = CommentModelStub.objects.none()

    class Meta:
        abstract = True


    @property
    def comments(self):
        """
        Return the visible comments.
        """
        if CommentModel is None:
            # No local comments, return empty queryset.
            # The project might be using DISQUS or Facebook comments instead.
            return CommentModelStub.objects.none()
        else:
            return CommentModel.objects.for_model(self).filter(is_public=True, is_removed=False)


    @property
    def comments_are_open(self):
        """
        Check if comments are open
        """
        if not self.enable_comments or CommentModel is None:
            return False

        try:
            # Get the moderator which is installed for this model.
            mod = moderator._registry[self.__class__]
        except KeyError:
            return True

        # Check the 'enable_field', 'auto_close_field' and 'close_after',
        # by reusing the basic Django policies.
        return CommentModerator.allow(mod, None, self, None)


    @property
    def comments_are_moderated(self):
        """
        Check if comments are moderated
        """
        try:
            # Get the moderator which is installed for this model.
            mod = moderator._registry[self.__class__]
        except KeyError:
            return False

        # Check the 'auto_moderate_field', 'moderate_after',
        # by reusing the basic Django policies.
        return CommentModerator.moderate(mod, None, self, None)


class CategoriesEntryMixin(models.Model):
    """
    Mixin for adding category support to a blog entry.
    """
    categories = models.ManyToManyField(appsettings.FLUENT_BLOGS_CATEGORY_MODEL, verbose_name=_("Categories"), blank=True)

    class Meta:
        abstract = True


class TagsEntryMixin(models.Model):
    """
    Mixin for adding tags to a blog entry
    """
    # Make association with tags optional.
    if TaggableManager is not None:
        tags = TaggableManager(blank=True)
    else:
        tags = None

    class Meta:
        abstract = True


class SeoEntryMixin(models.Model):
    """
    Mixin for adding SEO fields to a blog entry.
    """
    meta_keywords = models.CharField(_('keywords'), max_length=255, blank=True, default='', help_text=_("When this field is not filled in, the the tags will be used."))
    meta_description = models.CharField(_('description'), max_length=255, blank=True, default='', help_text=_("When this field is not filled in, the contents or intro text will be used."))

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


# Make sure the 'tags' field is ignored by South
try:
    from south.modelsinspector import add_ignored_fields
except ImportError:
    pass
else:
    # South should ignore the tags field as it's a RelatedField.
    add_ignored_fields((
        "^taggit\.managers\.TaggableManager",
        "^taggit_autocomplete_modified\.managers\.TaggableManagerAutocomplete",
    ))
