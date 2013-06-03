import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.urlresolvers import NoReverseMatch
from django.forms import ModelForm
from django.utils.translation import ugettext, ugettext_lazy as _
from fluent_blogs import appsettings
from fluent_blogs.base_models import AbstractEntryBase
from fluent_blogs.models import get_entry_model
from fluent_blogs.models.query import get_date_range
from fluent_blogs.utils.compat import now
from fluent_contents.admin import PlaceholderFieldAdmin


EntryModel = get_entry_model()


class AbstractEntryBaseAdminForm(ModelForm):
    """
    Base form for blog entries
    """
    def __init__(self, *args, **kwargs):
        super(AbstractEntryBaseAdminForm, self).__init__(*args, **kwargs)
        self.fields['publication_date'].required = False  # The admin's .save() method fills in a default.

    def clean(self):
        cleaned_data = super(AbstractEntryBaseAdminForm, self).clean()
        if 'slug' not in cleaned_data or 'publication_date' not in cleaned_data:
            return cleaned_data

        try:
            self.validate_unique_slug(cleaned_data)
        except ValidationError as e:
            self._errors['slug'] = self.error_class(e.messages)

        return cleaned_data

    def validate_unique_slug(self, cleaned_data):
        """
        Test whether the slug is unique within a given time period.
        """
        kwargs = {}
        error_msg = _("The slug is not unique")

        # The /year/month/slug/ URL determines when a slug can be unique.
        pubdate = cleaned_data['publication_date'] or now()
        if '{year}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            kwargs['year'] = pubdate.year
            error_msg = _("The slug is not unique within it's publication year.")
        if '{month}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            kwargs['month'] = pubdate.month
            error_msg = _("The slug is not unique within it's publication month.")
        if '{day}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            kwargs['day'] = pubdate.day
            error_msg = _("The slug is not unique within it's publication day.")

        date_range = get_date_range(**kwargs)
        if date_range:
            dup_qs = EntryModel.objects.filter(slug=cleaned_data['slug'], publication_date__range=date_range)
        else:
            dup_qs = EntryModel.objects.filter(slug=cleaned_data['slug'])

        if self.instance and self.instance.pk:
            dup_qs = dup_qs.exclude(pk=self.instance.pk)

        # Test whether the slug is unique in the current month
        # Note: doesn't take changes to FLUENT_BLOGS_ENTRY_LINK_STYLE into account.
        if dup_qs.exists():
            raise ValidationError(error_msg)


class AbstractEntryBaseAdmin(PlaceholderFieldAdmin):
    """
    The base functionality of the admin, which only uses the fields of the :class:`~fluent_blogs.base_models.AbstractEntryBase` model.
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

    FIELDSET_GENERAL = (None, {
        'fields': ('title', 'slug', 'status',),
    })
    FIELDSET_PUBLICATION = (_('Publication settings'), {
        'fields': ('publication_date', 'publication_end_date',),
        'classes': ('collapse',),
    })


    def save_model(self, request, obj, form, change):
        # Automatically store the user in the author field.
        if not change:
            obj.author = request.user

        if not obj.publication_date:
            # auto_now_add makes the field uneditable.
            # default fills the field before the post is written (too early)
            obj.publication_date = now()
        obj.save()


    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # When the page is accessed via a pagetype, warn that the node can't be previewed yet.
        context['preview_error'] = ''
        if 'fluent_pages' in settings.INSTALLED_APPS:
            from fluent_pages.urlresolvers import mixed_reverse, PageTypeNotMounted, MultipleReverseMatch
            try:
                mixed_reverse('entry_archive_index')
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
        if hasattr(entry, 'get_absolute_url') and entry.is_published:
            try:
                url = entry.get_absolute_url()
            except NoReverseMatch:
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


class EntryAdmin(AbstractEntryBaseAdmin):
    """
    The Django admin class for the default blog :class:`~fluent_blogs.models.Entry` model.
    When using a custom model, you can use :class:`AbstractEntryBaseAdmin`, which isn't attached to any of the optional fields.
    """
    # Redefine the fieldset, because it will be extended with auto-detected fields.
    FIELDSET_GENERAL = (None, {
        'fields': ('title', 'slug', 'status',),  # is filled with ('intro', 'contents', 'categories', 'tags', 'enable_comments') below
    })

    fieldsets = (
        FIELDSET_GENERAL,
        AbstractEntryBaseAdmin.FIELDSET_PUBLICATION,
    )


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'intro':
            kwargs['widget'] = widgets.AdminTextareaWidget(attrs={'rows': 4})
        return super(EntryAdmin, self).formfield_for_dbfield(db_field, **kwargs)


# Add all fields
_fields = EntryModel._meta.get_all_field_names()
for _f in ('intro', 'contents', 'categories', 'tags', 'enable_comments'):
    if _f in _fields:
        EntryAdmin.FIELDSET_GENERAL[1]['fields'] += (_f,)
