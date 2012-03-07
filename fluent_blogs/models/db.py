from django.conf import settings
from django.contrib import comments
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_contents.models.fields import PlaceholderField
from fluent_blogs.models.managers import EntryManager
from fluent_blogs import appsettings

# Optional tagging support
TaggableManager = None
if 'taggit_autocomplete_modified' in settings.INSTALLED_APPS:
    from taggit_autocomplete_modified.managers import TaggableManagerAutocomplete as TaggableManager
elif 'taggit' in settings.INSTALLED_APPS:
    from taggit.managers import TaggableManager


# Optional django-fluent-pages integration
def _mixed_reverse(viewname, args=None, kwargs=None):
    # Allow both stand-alone working, and integration with django-fluent-pages.
    # django-fluent-pages can't provide integration in the reverse-mapping unfortunately,
    # so it provides a separate reverse function that first checks the URLconf, then the CMS nodes.
    if 'fluent_pages' in settings.INSTALLED_APPS:
        from fluent_pages.urlresolvers import mixed_reverse
        return mixed_reverse(viewname, args=args, kwargs=kwargs, multiple=True).next()
    else:
        return reverse(viewname, args=args, kwargs=kwargs)


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
    contents = PlaceholderField("blog_contents")
    parent_site = models.ForeignKey(Site, editable=False, default=_get_current_site)

    status = models.CharField(_('status'), max_length=1, choices=STATUSES, default=DRAFT)
    publication_date = models.DateTimeField(_('publication date'), null=True, help_text=_('''When the page should go live, status must be "Published".'''))
    expire_date = models.DateTimeField(_('publication end date'), null=True, blank=True)

    # Metadata
    author = models.ForeignKey(User, verbose_name=_('author'), editable=False)
    creation_date = models.DateTimeField(_('creation date'), editable=False, auto_now_add=True)
    modification_date = models.DateTimeField(_('last modification'), editable=False, auto_now=True)

    objects = EntryManager()
    all_comments = GenericRelation(comments.get_model(), verbose_name=_("Comments"))
    categories = models.ManyToManyField(appsettings.FLUENT_BLOGS_CATEGORY_MODEL, verbose_name=_("Categories"), blank=True)

    if TaggableManager is not None:
        tags = TaggableManager(blank=True)
    else:
        tags = None


    class Meta:
        app_label = 'fluent_blogs'  # required for models subfolder
        verbose_name = _("Blog entry")
        verbose_name_plural = _("Blog entries")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        root = _mixed_reverse('entry_archive_index')
        return root + self.get_app_url()

    def get_app_url(self):
        return appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE.lstrip('/').format(
            year = self.publication_date.strftime('%Y'),
            month = self.publication_date.strftime('%m'),
            day = self.publication_date.strftime('%d'),
            slug = self.slug,
            pk = self.pk,
        )

    def get_short_url(self):
        return _mixed_reverse('entry_shortlink', kwargs={'pk': self.id})

    @property
    def comments(self):
        """Return the visible comments."""
        return comments.get_model().objects.for_model(self).filter(is_public=True)

    @property
    def comments_are_open(self):
        """Check if comments are open"""
        #if AUTO_CLOSE_COMMENTS_AFTER and self.comment_enabled:
        #    return (datetime.now() - self.start_publication).days <\
        #           AUTO_CLOSE_COMMENTS_AFTER
        #return self.comment_enabled
        return True

    @property
    def pingback_enabled(self):
        return False
