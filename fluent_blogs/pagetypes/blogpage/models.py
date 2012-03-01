from django.utils.translation import ugettext_lazy as _
from fluent_pages.models import Page


class BlogPage(Page):
    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
