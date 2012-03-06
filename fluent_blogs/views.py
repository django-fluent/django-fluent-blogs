from categories.models import Category
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.dates import DayArchiveView, MonthArchiveView, YearArchiveView, ArchiveIndexView
from django.views.generic.detail import DetailView, SingleObjectMixin
from fluent_blogs import appsettings
from fluent_blogs.models import Entry

base_queryset = Entry.objects.published()


class BaseBlogMixin(object):
    queryset = base_queryset
    context_object_name = None

    def get_context_data(self, **kwargs):
        context = super(BaseBlogMixin, self).get_context_data(**kwargs)
        context['FLUENT_BLOGS_BASE_TEMPLATE'] = appsettings.FLUENT_BLOGS_BASE_TEMPLATE
        if self.context_object_name:
            context[self.context_object_name] = getattr(self, self.context_object_name)  # e.g. author, category, tag
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


class EntryCategoryArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """
    template_name_suffix = '_archive_category'
    context_object_name = 'category'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return super(EntryCategoryArchive, self).get_queryset().filter(categories=self.category)


class EntryAuthorArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """
    template_name_suffix = '_archive_author'
    context_object_name = 'author'

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['slug'])
        return super(EntryAuthorArchive, self).get_queryset().filter(author=self.author)


class EntryTagArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """
    template_name_suffix = '_archive_tag'
    context_object_name = 'tag'

    def get_queryset(self):
        from taggit.models import Tag
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return super(EntryTagArchive, self).get_queryset().filter(tags=self.tag)
