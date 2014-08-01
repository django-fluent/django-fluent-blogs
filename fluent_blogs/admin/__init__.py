from django.contrib import admin
from .abstractbase import AbstractEntryBaseAdmin, AbstractTranslatableEntryBaseAdmin, SeoEntryAdminMixin
from .forms import AbstractEntryBaseAdminForm, AbstractTranslatableEntryBaseAdminForm
from .entryadmin import EntryAdmin
from fluent_blogs.models import get_entry_model, Entry

__all__ = (
    'AbstractEntryBaseAdminForm',
    'AbstractTranslatableEntryBaseAdminForm',

    'AbstractEntryBaseAdmin',
    'AbstractTranslatableEntryBaseAdmin',
    'SeoEntryAdminMixin',
    'EntryAdmin',
)


# Ony register the admin when the entry model is not customized.
if get_entry_model() is Entry:
    admin.site.register(Entry, EntryAdmin)
