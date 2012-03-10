from django.contrib import admin
from fluent_blogs.admin.entryadmin import EntryAdmin
from fluent_blogs.models import Entry

__all__ = (
    'EntryAdmin',
)

admin.site.register(Entry, EntryAdmin)
