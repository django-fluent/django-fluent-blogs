from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.views.generic.base import RedirectView
from django.views.generic.dates import (
    ArchiveIndexView,
    DayArchiveView,
    MonthArchiveView,
    YearArchiveView,
)
from django.views.generic.detail import DetailView, SingleObjectMixin
from fluent_utils.softdeps.fluent_pages import CurrentPageMixin, mixed_reverse
from parler.models import TranslatableModel, TranslationDoesNotExist
from parler.views import TranslatableSlugMixin

from fluent_blogs import appsettings
from fluent_blogs.models import get_entry_model
from fluent_blogs.models.query import get_category_for_slug, get_date_range


class BaseBlogMixin(CurrentPageMixin):
    context_object_name = None
    prefetch_translations = False
    view_url_name_paginated = None
    include_hidden = False

    def get_base_queryset(self, for_user=None):
        """The base queryset that all views derive from"""
        try:
            page = self.get_current_page()
        except AttributeError:
            # URL mounted view
            return get_entry_model().objects.published(
                for_user=for_user, include_hidden=self.include_hidden
            )
        else:
            # BlogPage mounted views
            return page.get_entry_queryset(
                view_url_name=self.view_url_name,
                for_user=for_user,
                include_hidden=self.include_hidden,
            )

    def get_queryset(self):
        # NOTE: This is also workaround, defining the queryset static somehow caused results to remain cached.
        qs = self.get_base_queryset()
        if self.prefetch_translations:
            qs = qs.prefetch_related("translations")
        return qs

    def get_language(self):
        """
        Return the language to display in this view.
        """
        return translation.get_language()  # Assumes that middleware has set this properly.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["FLUENT_BLOGS_BASE_TEMPLATE"] = appsettings.FLUENT_BLOGS_BASE_TEMPLATE
        context["HAS_DJANGO_FLUENT_COMMENTS"] = "fluent_comments" in settings.INSTALLED_APPS
        context[
            "FLUENT_BLOGS_INCLUDE_STATIC_FILES"
        ] = appsettings.FLUENT_BLOGS_INCLUDE_STATIC_FILES
        if self.context_object_name:
            context[self.context_object_name] = getattr(
                self, self.context_object_name
            )  # e.g. author, category, tag
        return context

    def get_view_url(self):
        # Support both use cases of the same view:
        if "page" in self.kwargs:
            view_url_name = self.view_url_name_paginated
        else:
            view_url_name = self.view_url_name
        return mixed_reverse(
            view_url_name, args=self.args, kwargs=self.kwargs, current_page=self.get_current_page()
        )


class BaseArchiveMixin(BaseBlogMixin):
    date_field = "publication_date"
    month_format = "%m"
    allow_future = False
    paginate_by = appsettings.FLUENT_BLOGS_PAGINATE_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.active_translations(
            self.get_language()
        )  # NOTE: can't combine with other filters on translations__ relation.

        # Reapply ordering of MultipleObjectMixin that was skipped;
        # The BaseDateListView.get_ordering() turns this into a default DESC on the date field.
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_template_names(self):
        names = super().get_template_names()

        # Include the appname/model_suffix.html version for any customized model too.
        if not names[-1].startswith("fluent_blogs/entry"):
            names.append(f"fluent_blogs/entry{self.template_name_suffix}.html")

        return names


class BaseDetailMixin(TranslatableSlugMixin, BaseBlogMixin):
    # Only relevant at the detail page, e.g. for a language switch menu.
    prefetch_translations = appsettings.FLUENT_BLOGS_PREFETCH_TRANSLATIONS
    include_hidden = True  # only visible with direct link

    def get_queryset(self):
        # The DetailView redefines get_queryset() to show detail pages for staff members.
        # All other overviews won't show the draft pages yet.
        qs = self.get_base_queryset(for_user=self.request.user)
        if self.prefetch_translations:
            qs = qs.prefetch_related("translations")

        # Allow same slug in different dates
        # The available arguments depend on the FLUENT_BLOGS_ENTRY_LINK_STYLE setting.
        year = int(self.kwargs["year"]) if "year" in self.kwargs else None
        month = int(self.kwargs["month"]) if "month" in self.kwargs else None
        day = int(self.kwargs["day"]) if "day" in self.kwargs else None

        range = get_date_range(year, month, day)
        if range:
            qs = qs.filter(publication_date__range=range)

        return qs

    def get_object(self, queryset=None):
        if issubclass(get_entry_model(), TranslatableModel):
            # Filter by slug and language
            # Note that translation support is still optional,
            # even though the class inheritance includes it.
            return TranslatableSlugMixin.get_object(self, queryset)
        else:
            # Regular slug check, skip TranslatableSlugMixin
            return SingleObjectMixin.get_object(self, queryset)

    def get_language_choices(self):
        return appsettings.FLUENT_BLOGS_LANGUAGES.get_active_choices()

    def get_template_names(self):
        names = super().get_template_names()

        if not names[-1].startswith("fluent_blogs/entry"):
            names.append(f"fluent_blogs/entry{self.template_name_suffix}.html")

        return names


class EntryArchiveIndex(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive index page.
    """

    view_url_name = "entry_archive_index"
    view_url_name_paginated = "entry_archive_index_paginated"
    template_name_suffix = "_archive_index"
    allow_empty = True


class EntryYearArchive(BaseArchiveMixin, YearArchiveView):
    view_url_name = "entry_archive_year"
    make_object_list = True


class EntryMonthArchive(BaseArchiveMixin, MonthArchiveView):
    view_url_name = "entry_archive_month"


class EntryDayArchive(BaseArchiveMixin, DayArchiveView):
    view_url_name = "entry_archive_day"


class EntryDetail(BaseDetailMixin, DetailView):
    """
    Blog detail page.
    """

    view_url_name = "entry_detail"


class EntryShortLink(SingleObjectMixin, RedirectView):
    permanent = False  # Allow changing the URL format

    def get_queryset(self):
        # NOTE: This is a workaround, defining the queryset static somehow caused results to remain cached.
        return get_entry_model().objects.published()

    def get_redirect_url(self, **kwargs):
        entry = self.get_object()
        try:
            return entry.get_absolute_url()
        except TranslationDoesNotExist as e:
            # Some entries may not have a language for the current site/subpath.
            raise Http404(str(e))


class EntryCategoryArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """

    view_url_name = "entry_archive_category"
    view_url_name_paginated = "entry_archive_category_paginated"
    template_name_suffix = "_archive_category"
    context_object_name = "category"

    def dispatch(self, request, *args, **kwargs):
        self.category = self.get_category(slug=self.kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(categories=self.category)

    def get_category(self, slug):
        """
        Get the category object
        """
        try:
            return get_category_for_slug(slug)
        except ObjectDoesNotExist as e:
            raise Http404(str(e))


class EntryAuthorArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """

    view_url_name = "entry_archive_author"
    view_url_name_paginated = "entry_archive_author_paginated"
    template_name_suffix = "_archive_author"
    context_object_name = "author"

    def dispatch(self, request, *args, **kwargs):
        self.author = self.get_user(slug=self.kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(author=self.author)

    def get_user(self, slug):
        User = get_user_model()
        return get_object_or_404(User, **{User.USERNAME_FIELD: slug})


class EntryTagArchive(BaseArchiveMixin, ArchiveIndexView):
    """
    Archive based on tag.
    """

    view_url_name = "entry_archive_tag"
    view_url_name_paginated = "entry_archive_tag_paginated"
    template_name_suffix = "_archive_tag"
    context_object_name = "tag"

    def dispatch(self, request, *args, **kwargs):
        self.tag = self.get_tag(slug=self.kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(tags=self.tag)

    def get_tag(self, slug):
        from taggit.models import Tag  # django-taggit is optional, hence imported here.

        return get_object_or_404(Tag, slug=slug)
