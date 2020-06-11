from django.utils.translation import ugettext_lazy as _
from fluent_pages.integration.fluent_contents.models import FluentContentsPage
from parler.models import TranslatableModel
from parler.utils.context import switch_language

from fluent_blogs.models import get_entry_model


class BlogPage(FluentContentsPage):

    class Meta:
        verbose_name = _("Blog module")
        verbose_name_plural = _("Blog modules")

    @property
    def entries(self):
        """
        Return the entries that are published under this node.
        """
        # Since there is currently no filtering in place, return all entries.
        EntryModel = get_entry_model()
        qs = get_entry_model().objects.order_by('-publication_date')

        # Only limit to current language when this makes sense.
        if issubclass(EntryModel, TranslatableModel):
            admin_form_language = self.get_current_language()  # page object is in current language tab.
            qs = qs.active_translations(admin_form_language).language(admin_form_language)

        return qs

    def get_entry_queryset(self, view_url_name, for_user=None, include_hidden=False):
        """
        Return the base queryset that will be shown at this blog page.
        This allows subclasses of the `BlogPage` to limit which pages
        are shown at a particular mount point.
        """
        return get_entry_model().objects.published(for_user=for_user, include_hidden=include_hidden)

    def get_entry_url(self, entry):
        """
        Return the URL of a blog entry, relative to this page.
        """
        # It could be possible this page is fetched as fallback, while the 'entry' does have a translation.
        # - Currently django-fluent-pages 1.0b3 `Page.objects.get_for_path()` assigns the language of retrieval
        #   as current object language. The page is not assigned a fallback language instead.
        # - With i18n_patterns() that would make strange URLs, such as '/en/blog/2016/05/dutch-entry-title/'
        # Hence, respect the entry language as starting point to make the language consistent.
        with switch_language(self, entry.get_current_language()):
            return self.get_absolute_url() + entry.get_relative_url()
