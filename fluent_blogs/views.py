from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.dates import DayArchiveView, MonthArchiveView, YearArchiveView, ArchiveIndexView
from django.views.generic.detail import DetailView, SingleObjectMixin
from fluent_blogs import appsettings
from fluent_blogs.models import Entry

base_queryset = Entry.objects.published()


class BaseBlogMixin(object):
    queryset = base_queryset

    def get_context_data(self, **kwargs):
        context = super(BaseBlogMixin, self).get_context_data(**kwargs)
        context['FLUENT_BLOGS_BASE_TEMPLATE'] = appsettings.FLUENT_BLOGS_BASE_TEMPLATE
        return context


class BaseArchiveMixin(BaseBlogMixin):
    date_field = 'publication_date'
    month_format = '%m'
    allow_future = False
    paginate_by = 10


class EntryArchiveIndex(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive index page.
    """
    allow_empty = True


class EntryYearArchive(BaseArchiveMixin, YearArchiveView):
    make_object_list = True


class EntryMonthArchive(BaseArchiveMixin, MonthArchiveView):
    pass


class EntryDayArchive(BaseArchiveMixin, DayArchiveView):
    pass


class EntryDetail(BaseBlogMixin, DetailView):
    """
    Blog detail page.
    """
    queryset = base_queryset


class EntryShortLink(SingleObjectMixin, RedirectView):
    queryset = base_queryset
    permanent = True

    def get_redirect_url(self, **kwargs):
        entry = self.get_object()
        return entry.get_absolute_url()


class EntryTagArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """

    def get_queryset(self):
        from taggit.models import Tag
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return super(EntryTagArchive, self).get_queryset().filter(tags=self.tag)


    def get_context_data(self, **kwargs):
        context = super(EntryTagArchive, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        return context
