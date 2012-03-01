from datetime import datetime
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from fluent_contents.admin.placeholderfield import PlaceholderFieldAdmin
from fluent_blogs.models import Entry


class EntryAdmin(PlaceholderFieldAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'status', 'contents',),
        }),
        (_('Publication settings'), {
            'fields': ('publication_date', 'expire_date',),
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


admin.site.register(Entry, EntryAdmin)
