from datetime import datetime
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets
from django.utils.translation import ugettext_lazy as _
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin
from fluent_blogs.models import Entry


class EntryAdmin(PlaceholderFieldAdmin):
    list_display = ('title', 'status_column', 'modification_date', 'actions_column')
    list_filter = ('status',)
    date_hierarchy = 'publication_date'
    search_fields = ('slug', 'title')
    actions = ['make_published']

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
            obj.publication_date = datetime.now()
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
                pass

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


    def status_column(self, entry):
        status = entry.status
        title = [rec[1] for rec in Entry.STATUSES if rec[0] == status].pop()
        icon  = [rec[1] for rec in self.STATUS_ICONS if rec[0] == status].pop()
        if hasattr(settings, 'ADMIN_MEDIA_PREFIX'):
            admin = settings.ADMIN_MEDIA_PREFIX + 'img/admin/'  # Django 1.3
        elif getattr(settings, 'STATIC_URL', None):
            admin = settings.STATIC_URL + 'admin/img/'  # Django 1.4+
        return u'<img src="{admin}{icon}" width="10" height="10" alt="{title}" title="{title}" />'.format(admin=admin, icon=icon, title=title)

    status_column.allow_tags = True
    status_column.short_description = _('Status')


    def actions_column(self, entry):
        return u' '.join(self._actions_column_icons(entry))

    actions_column.allow_tags = True
    actions_column.short_description = _('Actions')


    def _actions_column_icons(self, entry):
        actions = []
        if hasattr(entry, 'get_absolute_url') and entry.is_published:
            actions.append(
                u'<a href="{url}" title="{title}" target="_blank"><img src="{static}fluent_pages/img/admin/world.gif" width="16" height="16" alt="{title}" /></a>'.format(
                    url=entry.get_absolute_url(), title=_('View on site'), static=settings.STATIC_URL)
            )
        return actions


    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=Entry.PUBLISHED)

        if rows_updated == 1:
            message = "1 entry was marked as published."
        else:
            message = "{0} entries were marked as published.".format(rows_updated)
        self.message_user(request, message)


    make_published.short_description = _("Mark selected entries as published")
