from django.utils.translation import ugettext_lazy as _
from fluent_pages.integration.fluent_contents import FluentContentsPage
from fluent_blogs.models import get_entry_model
from parler.models import TranslatableModel


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

    def get_entry_url(self, entry):
        """
        Return the URL of a blog entry, relative to this page.
        """
        return self.get_absolute_url() + entry.get_relative_url()
