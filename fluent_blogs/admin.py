from datetime import datetime
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin
from fluent_blogs.models import Entry


class EntryAdmin(PlaceholderFieldAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'status', 'contents', 'categories'),
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
            from fluent_pages.urlresolvers import mixed_reverse, PageTypeNotMounted
            try:
                mixed_reverse('entry_archive_index')
            except PageTypeNotMounted:
                context['preview_error'] = _("The blog page can't be previewed yet, a 'Blog' page needs to be created first.")

        return super(EntryAdmin, self).render_change_form(request, context, add, change, form_url, obj)


admin.site.register(Entry, EntryAdmin)
