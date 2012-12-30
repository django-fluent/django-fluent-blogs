from datetime import datetime
import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin
from fluent_blogs.models import Entry

# The timezone support was introduced in Django 1.4, fallback to standard library for 1.3.
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


class EntryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['publication_date'].required = False  # The admin's .save() method fills in a default.


class EntryAdmin(PlaceholderFieldAdmin):
    list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    list_filter = ('status',)
    date_hierarchy = 'publication_date'
    search_fields = ('slug', 'title')
    actions = ['make_published']
    form = EntryForm

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'status', 'intro', 'contents', 'categories'),
        }),
        (_('Publication settings'), {
            'fields': ('publication_date', 'publication_end_date',),
            'classes': ('collapse',),
        }),
    )

    if Entry.tags is not None:
        fieldsets[0][1]['fields'] += ('tags',)

    fieldsets[0][1]['fields'] += ('enable_comments',)

    prepopulated_fields = {'slug': ('title',),}
    radio_fields = {
        'status': admin.HORIZONTAL,
    }


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
                context['preview_error'] = _("The blog entry can't be previewed yet, a 'Blog' page needs to be created first.")
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

        return super(EntryAdmin, self).render_change_form(request, context, add, change, form_url, obj)


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'intro':
            kwargs['widget'] = widgets.AdminTextareaWidget(attrs={'rows': 4})
        return super(EntryAdmin, self).formfield_for_dbfield(db_field, **kwargs)



    # ---- List code ----

    STATUS_ICONS = (
        (Entry.PUBLISHED, 'icon-yes.gif'),
        (Entry.DRAFT,     'icon-unknown.gif'),
    )


    @classmethod
    def get_status_column(cls, entry):
        # Create a status column, is also reused by templatetags/fluent_blogs_admin_tags.py
        status = entry.status
        title = next(rec[1] for rec in Entry.STATUSES if rec[0] == status)
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
        rows_updated = queryset.update(status=Entry.PUBLISHED)

        if rows_updated == 1:
            message = "1 entry was marked as published."
        else:
            message = "{0} entries were marked as published.".format(rows_updated)
        self.message_user(request, message)


    make_published.short_description = _("Mark selected entries as published")
