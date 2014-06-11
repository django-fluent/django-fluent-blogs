import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.urlresolvers import NoReverseMatch
from django.forms import ModelForm
from django.utils.translation import ugettext, ugettext_lazy as _
from fluent_blogs import appsettings
from fluent_blogs.base_models import AbstractEntryBase
from fluent_blogs.models import get_entry_model, Entry_Translation
from fluent_blogs.models.query import get_date_range
from fluent_blogs.utils.compat import now
from fluent_contents.admin import PlaceholderFieldAdmin
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from parler.models import TranslatableModel, TranslationDoesNotExist


EntryModel = get_entry_model()


class AbstractEntryBaseAdminForm(ModelForm):
    """
    Base form for blog entries
    """
    def __init__(self, *args, **kwargs):
        super(AbstractEntryBaseAdminForm, self).__init__(*args, **kwargs)

        # The admin's .save() method fills in a default:
        self.fields['publication_date'].required = False
        try:
            author_field = self.fields['author']
        except KeyError:
            pass
        else:
            author_field.required = False
            self.initial.setdefault('author', author_field.user)

    def clean(self):
        cleaned_data = super(AbstractEntryBaseAdminForm, self).clean()
        if 'slug' not in cleaned_data or 'publication_date' not in cleaned_data:
            return cleaned_data

        try:
            self.validate_unique_slug(cleaned_data)
        except ValidationError as e:
            self._errors['slug'] = self.error_class(e.messages)

        return cleaned_data

    def clean_author(self):
        # Make sure the form never assigns None to the author value.
        return self.cleaned_data['author'] or self.fields['author'].user

    def validate_unique_slug(self, cleaned_data):
        """
        Test whether the slug is unique within a given time period.
        """
        date_kwargs = {}
        error_msg = _("The slug is not unique")

        # The /year/month/slug/ URL determines when a slug can be unique.
        pubdate = cleaned_data['publication_date'] or now()
        if '{year}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            date_kwargs['year'] = pubdate.year
            error_msg = _("The slug is not unique within it's publication year.")
        if '{month}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            date_kwargs['month'] = pubdate.month
            error_msg = _("The slug is not unique within it's publication month.")
        if '{day}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            date_kwargs['day'] = pubdate.day
            error_msg = _("The slug is not unique within it's publication day.")

        date_range = get_date_range(**date_kwargs)

        # Base filters are configurable for translation support.
        dup_filters = self.get_unique_slug_filters(cleaned_data)
        if date_range:
            dup_filters['publication_date__range'] = date_range

        dup_qs = EntryModel.objects.filter(**dup_filters)

        if self.instance and self.instance.pk:
            dup_qs = dup_qs.exclude(pk=self.instance.pk)

        # Test whether the slug is unique in the current month
        # Note: doesn't take changes to FLUENT_BLOGS_ENTRY_LINK_STYLE into account.
        if dup_qs.exists():
            raise ValidationError(error_msg)

    def get_unique_slug_filters(self, cleaned_data):
        # Allow to override this for translations
        return {
            'slug': cleaned_data['slug'],
        }



class AbstractTranslatableEntryBaseAdminForm(TranslatableModelForm, AbstractEntryBaseAdminForm):
    """
    Base form for translatable blog entries
    """
    def get_unique_slug_filters(self, cleaned_data):
        return {
            'translations__slug': cleaned_data['slug'],
            'translations__language_code': self.language_code
        }



class AbstractEntryBaseAdmin(PlaceholderFieldAdmin):
    """
    The base functionality of the admin, which only uses the fields of the
    :class:`~fluent_blogs.base_models.AbstractEntryBase` model.
    Everything else is branched off in the :class:`EntryAdmin` class.
    """
    list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    list_filter = ('status',)
    date_hierarchy = 'publication_date'
    search_fields = ('slug', 'title')
    actions = ['make_published']
    form = AbstractEntryBaseAdminForm
    prepopulated_fields = {'slug': ('title',),}
    radio_fields = {
        'status': admin.HORIZONTAL,
    }
    raw_id_fields = ('author',)

    FIELDSET_GENERAL = (None, {
        'fields': ('title', 'slug', 'status',),
    })
    FIELDSET_PUBLICATION = (_('Publication settings'), {
        'fields': ('publication_date', 'publication_end_date', 'author'),
        'classes': ('collapse',),
    })


    class Media:
        css = {
            'all': ('fluent_blogs/admin/admin.css',)
        }


    def queryset(self, request):
        qs = super(AbstractEntryBaseAdmin, self).queryset(request)

        # Admin only shows current site for now,
        # until there is decent filtering for it.
        if appsettings.FLUENT_BLOGS_FILTER_SITE_ID:
            qs = qs.filter(parent_site=settings.SITE_ID)
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(AbstractEntryBaseAdmin, self).get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly_fields.append('author')
        return readonly_fields

    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not obj.author_id:
            obj.author = request.user

        if not obj.publication_date:
            # auto_now_add makes the field uneditable.
            # default fills the field before the post is written (too early)
            obj.publication_date = now()
        obj.save()


    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Allow formfield_overrides to contain field names too.
        """
        overrides = self.formfield_overrides.get(db_field.name)
        if overrides:
            kwargs.update(overrides)

        field = super(AbstractEntryBaseAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        # Pass user to the form.
        if db_field.name == 'author':
            field.user = kwargs['request'].user
        return field


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # When the page is accessed via a pagetype, warn that the node can't be previewed yet.
        context['preview_error'] = ''
        if 'fluent_pages' in settings.INSTALLED_APPS:
            from fluent_pages.urlresolvers import PageTypeNotMounted, MultipleReverseMatch
            try:
                self._reverse_blogpage_index(request, obj)
            except PageTypeNotMounted:
                from fluent_blogs.pagetypes.blogpage.models import BlogPage
                context['preview_error'] = ugettext("The blog entry can't be previewed yet, a '{page_type_name}' page needs to be created first.").format(page_type_name=BlogPage._meta.verbose_name)
            except MultipleReverseMatch:
                # When 'entry_archive_index is ambiguous (because there are multiple blog nodes in the fluent-pages tree),
                # the edit page will automatically pick an option.
                pass
            except NoReverseMatch:
                # Since forgetting the pagetype app is easy, give off a warning to help developers
                # find their way with these apps.
                raise ImproperlyConfigured(
                    "To use django-fluent-blogs, either include('fluent_blogs.urls') in the URLConf, "
                    "or add the 'fluent_blogs.pagetypes.blogpage' app to the INSTALLED_APPS."
                )

        return super(AbstractEntryBaseAdmin, self).render_change_form(request, context, add, change, form_url, obj)


    def _reverse_blogpage_index(self, request, obj=None):
        # Internal method with "protected access" to handle translation differences.
        # This is only called when 'fluent_pages' is in the INSTALLED_APPS.
        from fluent_pages.urlresolvers import mixed_reverse
        return mixed_reverse('entry_archive_index')


    # ---- List code ----

    STATUS_ICONS = (
        (AbstractEntryBase.PUBLISHED, 'icon-yes.gif'),
        (AbstractEntryBase.DRAFT,     'icon-unknown.gif'),
    )


    @classmethod
    def get_status_column(cls, entry):
        # Create a status column, is also reused by templatetags/fluent_blogs_admin_tags.py
        status = entry.status
        title = next(rec[1] for rec in AbstractEntryBase.STATUSES if rec[0] == status)
        icon  = next(rec[1] for rec in cls.STATUS_ICONS if rec[0] == status)
        if django.VERSION >= (1, 4):
            admin = settings.STATIC_URL + 'admin/img/'
        else:
            admin = settings.ADMIN_MEDIA_PREFIX + 'img/admin/'
        return u'<img src="{admin}{icon}" width="10" height="10" alt="{title}" title="{title}" />'.format(admin=admin, icon=icon, title=title)


    def status_column(self, entry):
        # Method is needed because can't assign attributes to a class method
        return self.get_status_column(entry)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    @classmethod
    def get_actions_column(cls, entry):
        return u' '.join(cls._actions_column_icons(entry))


    @classmethod
    def _actions_column_icons(cls, entry):
        actions = []
        if cls.can_preview_object(entry):
            try:
                url = entry.get_absolute_url()
            except (NoReverseMatch, TranslationDoesNotExist):
                # A Blog Entry is already added, but the URL can no longer be resolved.
                # This can either mean that urls.py is missing a 'fluent_blogs.urls' (unlikely),
                # or that this is a PageTypeNotMounted exception because the "Blog page" node was removed.
                # In the second case, the edit page should still be reachable, and the "view on site" link will give an alert.
                pass
            else:
                actions.append(
                    u'<a href="{url}" title="{title}" target="_blank"><img src="{static}fluent_blogs/img/admin/world.gif" width="16" height="16" alt="{title}" /></a>'.format(
                        url=url, title=_('View on site'), static=settings.STATIC_URL)
                )
        return actions


    @classmethod
    def can_preview_object(cls, entry):
        """ Override whether the node can be previewed. """
        return hasattr(entry, 'get_absolute_url') and entry.is_published


    def actions_column(self, entry):
        return self.get_actions_column(entry)

    actions_column.allow_tags = True
    actions_column.short_description = _('Actions')


    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=AbstractEntryBase.PUBLISHED)

        if rows_updated == 1:
            message = "1 entry was marked as published."
        else:
            message = "{0} entries were marked as published.".format(rows_updated)
        self.message_user(request, message)

    make_published.short_description = _("Mark selected entries as published")



class AbstractTranslatableEntryBaseAdmin(TranslatableAdmin, AbstractEntryBaseAdmin):
    """
    The base functionality of the admin, which only uses the fields of the
    :class:`~fluent_blogs.base_models.AbstractTranslatedEntryBase` model.
    Everything else is branched off in the :class:`EntryAdmin` class.
    """
    form = AbstractTranslatableEntryBaseAdminForm
    list_display = ('title', 'language_column', 'status_column', 'modification_date', 'actions_column')
    search_fields = ('translations__slug', 'translations__title')
    prepopulated_fields = {}  # Not supported by django-parler 0.9.2, using get_prepopulated_fields() as workaround.

    def get_prepopulated_fields(self, request, obj=None):
        # Still allow to override self.prepopulated_fields in other custom classes,
        # but default to the settings which are compatible with django-parler.
        return self.prepopulated_fields or {'slug': ('title',),}

    def _reverse_blogpage_index(self, request, obj=None):
        # Updated mixed_reverse() call, with language code included.
        from fluent_pages.urlresolvers import mixed_reverse
        language_code = self.get_form_language(request, obj)
        return mixed_reverse('entry_archive_index', language_code=language_code)

    def get_language_short_title(self, language_code):
        """
        Turn the language code to uppercase.
        """
        return language_code.upper()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['FLUENT_BLOGS_IS_TRANSLATABLE'] = True
        return super(AbstractTranslatableEntryBaseAdmin, self).changelist_view(request, extra_context)


_model_fields = EntryModel._meta.get_all_field_names()
if issubclass(EntryModel, TranslatableModel):
    _entry_admin_base = AbstractTranslatableEntryBaseAdmin
    _model_fields += Entry_Translation.get_translated_fields()
else:
    _entry_admin_base = AbstractEntryBaseAdmin


class SeoEntryAdminMixin(object):
    """
    Mixin for the SEO fields.
    """
    FIELDSET_SEO = (_('SEO settings'), {
        'fields': ('meta_keywords', 'meta_description'),
        'classes': ('collapse',),
    })

    # AbstractEntryBaseAdmin allows to specify the widgets by field name,
    # which formfield_overrides doesn't support by default.
    formfield_overrides = {
        'meta_keywords': {
            'widget': AdminTextInputWidget(attrs={'class': 'vLargeTextField'})
        },
        'meta_description': {
            'widget': AdminTextareaWidget(attrs={'rows': 3})
        },
    }


class EntryAdmin(SeoEntryAdminMixin, _entry_admin_base):
    """
    The Django admin class for the default blog :class:`~fluent_blogs.models.Entry` model.
    When using a custom model, you can use :class:`AbstractEntryBaseAdmin`, which isn't attached to any of the optional fields.
    """
    # Redefine the fieldset, because it will be extended with auto-detected fields.
    FIELDSET_GENERAL = (None, {
        'fields': ('title', 'slug', 'status',),  # is filled with ('intro', 'contents', 'categories', 'tags', 'enable_comments') below
    })

    # For Django 1.4, the fieldsets shouldn't be declared with 'fieldsets ='
    # as the admin validation won't recognize the translated fields.
    # The 1.4 validation didn't check the form at all, but only checks the model fields.
    # As of Django 1.5, using 'fieldsets = ..' with translated fields just works.
    declared_fieldsets = (
        FIELDSET_GENERAL,
        AbstractEntryBaseAdmin.FIELDSET_PUBLICATION,
        SeoEntryAdminMixin.FIELDSET_SEO,
    )

    formfield_overrides = {}
    formfield_overrides.update(SeoEntryAdminMixin.formfield_overrides)
    formfield_overrides.update({
        'intro': {
            'widget': widgets.AdminTextareaWidget(attrs={'rows': 4})
        },
    })


# Add all fields
for _f in ('intro', 'contents', 'categories', 'tags', 'enable_comments'):
    if _f in _model_fields:
        EntryAdmin.FIELDSET_GENERAL[1]['fields'] += (_f,)
