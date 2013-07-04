from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from django.views.generic.dates import DayArchiveView, MonthArchiveView, YearArchiveView, ArchiveIndexView
from django.views.generic.detail import DetailView, SingleObjectMixin
from fluent_blogs import appsettings
from fluent_blogs.models import get_entry_model, get_category_model
from fluent_blogs.models.query import get_date_range
from fluent_blogs.utils.compat import get_user_model


class BaseBlogMixin(object):
    context_object_name = None

    def get_queryset(self):
        # NOTE: This is a workaround, defining the queryset static somehow caused results to remain cached.
        return get_entry_model().objects.published()

    def get_context_data(self, **kwargs):
        context = super(BaseBlogMixin, self).get_context_data(**kwargs)
        context['FLUENT_BLOGS_BASE_TEMPLATE'] = appsettings.FLUENT_BLOGS_BASE_TEMPLATE
        context['HAS_DJANGO_FLUENT_COMMENTS'] = 'fluent_comments' in settings.INSTALLED_APPS
        context['FLUENT_BLOGS_INCLUDE_STATIC_FILES'] = appsettings.FLUENT_BLOGS_INCLUDE_STATIC_FILES
        if self.context_object_name:
            context[self.context_object_name] = getattr(self, self.context_object_name)  # e.g. author, category, tag
        return context


class BaseArchiveMixin(BaseBlogMixin):
    date_field = 'publication_date'
    month_format = '%m'
    allow_future = False
    paginate_by = 10

    def get_template_names(self):
        names = super(BaseArchiveMixin, self).get_template_names()

        # Include the appname/model_suffix.html version for any customized model too.
        if not names[-1].startswith('fluent_blogs/entry'):
            names.append("fluent_blogs/entry{0}.html".format(self.template_name_suffix))

        return names


class BaseDetailMixin(BaseBlogMixin):
    def get_queryset(self):
        qs = super(BaseDetailMixin, self).get_queryset()

        # Allow same slug in different dates
        # The available arguments depend on the FLUENT_BLOGS_ENTRY_LINK_STYLE setting.
        year = int(self.kwargs['year']) if 'year' in self.kwargs else None
        month = int(self.kwargs['month']) if 'month' in self.kwargs else None
        day = int(self.kwargs['day']) if 'day' in self.kwargs else None

        range = get_date_range(year, month, day)
        if range:
            qs = qs.filter(publication_date__range=range)

        return qs

    def get_template_names(self):
        names = super(BaseDetailMixin, self).get_template_names()

        if not names[-1].startswith('fluent_blogs/entry'):
            names.append("fluent_blogs/entry{0}.html".format(self.template_name_suffix))

        return names


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


class EntryDetail(BaseDetailMixin, DetailView):
    """
    Blog detail page.
    """
    pass


class EntryShortLink(SingleObjectMixin, RedirectView):
    permanent = False   # Allow changing the URL format

    def get_queryset(self):
        # NOTE: This is a workaround, defining the queryset static somehow caused results to remain cached.
        return get_entry_model().objects.published()

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
        self.category = get_object_or_404(get_category_model(), slug=self.kwargs['slug'])
        return super(EntryCategoryArchive, self).get_queryset().filter(categories=self.category)


class EntryAuthorArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """
    template_name_suffix = '_archive_author'
    context_object_name = 'author'

    def get_queryset(self):
        self.author = get_object_or_404(get_user_model(), username=self.kwargs['slug'])
        return super(EntryAuthorArchive, self).get_queryset().filter(author=self.author)


class EntryTagArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """
    template_name_suffix = '_archive_tag'
    context_object_name = 'tag'

    def get_queryset(self):
        from taggit.models import Tag  # django-taggit is optional, hence imported here.
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return super(EntryTagArchive, self).get_queryset().filter(tags=self.tag)
