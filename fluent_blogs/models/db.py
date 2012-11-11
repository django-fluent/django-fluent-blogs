from django.conf import settings
from django.contrib import comments
from django.contrib.comments.moderation import moderator, CommentModerator
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.fields import PlaceholderField
from fluent_blogs.urlresolvers import blog_reverse
from fluent_blogs.models.managers import EntryManager
from fluent_blogs import appsettings

# Optional tagging support
TaggableManager = None
if 'taggit_autocomplete_modified' in settings.INSTALLED_APPS:
    from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
elif 'taggit' in settings.INSTALLED_APPS:
    from taggit.managers import TaggableManager


def _get_current_site():
    return Site.objects.get_current()



class Entry(models.Model):
    # Some publication states
    DRAFT = 'd'
    PUBLISHED = 'p'
    STATUSES = (
        (PUBLISHED, _('Published')),
        (DRAFT, _('Draft')),
    )

    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"))
    intro = models.TextField(_("Introtext"))
    contents = PlaceholderField("blog_contents")
    parent_site = models.ForeignKey(Site, editable=False, default=_get_current_site)

    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT, db_index=True)
    publication_date = models.DateTimeField(_('publication date'), null=True, db_index=True, help_text=_('''When the entry should go live, status must be "Published".'''))
    publication_end_date = models.DateTimeField(_('publication end date'), null=True, blank=True, db_index=True)

    # Metadata
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    objects = EntryManager()
    all_comments = GenericRelation(comments.get_model(), verbose_name=_("Comments"), object_id_field='object_pk')
    categories = models.ManyToManyField(appsettings.FLUENT_BLOGS_CATEGORY_MODEL, verbose_name=_("Categories"), blank=True)
    enable_comments = models.BooleanField(_("Enable comments"), default=True)

    if TaggableManager is not None:
        tags = TaggableManager(blank=True)
    else:
        tags = None


    class Meta:
        app_label = 'fluent_blogs'  # required for models subfolder
        verbose_name = _("Blog entry")
        verbose_name_plural = _("Blog entries")
        ordering = ('-publication_date',)
        get_latest_by = "publication_date"  # Support Entry.objects.latest() call.


    def __unicode__(self):
        return self.title


    def get_absolute_url(self):
        root = blog_reverse('entry_archive_index', ignore_multiple=True)
        return root + self._get_relative_url()


    def _get_relative_url(self):
        # Return the link style, using the permalink style setting.
        return appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE.lstrip('/').format(
            year = self.publication_date.strftime('%Y'),
            month = self.publication_date.strftime('%m'),
            day = self.publication_date.strftime('%d'),
            slug = self.slug,
            pk = self.pk,
        )


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
    def comments(self):
        """
        Return the visible comments.
        """
        return comments.get_model().objects.for_model(self).filter(is_public=True)


    @property
    def comments_are_open(self):
        """
        Check if comments are open
        """
        if not self.enable_comments:
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
    def previous_entry(self):
        """
        Return the previous entry
        """
        entries = self.__class__.objects.published().filter(publication_date__lt=self.publication_date).order_by('-publication_date')[:1]
        return entries[0] if entries else None


    @property
    def next_entry(self):
        """
        Return the next entry
        """
        entries = self.__class__.objects.published().filter(publication_date__gt=self.publication_date).order_by('publication_date')[:1]
        return entries[0] if entries else None



# Auto-register with django-fluent-comments moderation
if 'fluent_comments' in settings.INSTALLED_APPS:
    from fluent_comments.moderation import moderate_model
    moderate_model(Entry,
        publication_date_field='publication_date',
        enable_comments_field='enable_comments',
    )


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
