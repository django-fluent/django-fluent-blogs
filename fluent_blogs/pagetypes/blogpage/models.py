from django.utils.translation import ugettext_lazy as _
from fluent_blogs.models import Entry
from fluent_pages.models import Page


class BlogPage(Page):
    class Meta:
        verbose_name = _("Blog module")
        verbose_name_plural = _("Blog modules")


    @property
    def entries(self):
        """
        Return the entries that are published under this node.
        """
        # Since there is currently no filtering in place, return all entries.
        return Entry.objects.all().order_by('-publication_date')
