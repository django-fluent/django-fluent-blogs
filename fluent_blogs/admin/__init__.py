from django.contrib import admin

from fluent_blogs.models import Entry, get_entry_model

from .abstractbase import (
    AbstractEntryBaseAdmin,
    AbstractTranslatableEntryBaseAdmin,
    SeoEntryAdminMixin,
)
from .entryadmin import EntryAdmin
from .forms import AbstractEntryBaseAdminForm, AbstractTranslatableEntryBaseAdminForm

__all__ = (
    "AbstractEntryBaseAdminForm",
    "AbstractTranslatableEntryBaseAdminForm",
    "AbstractEntryBaseAdmin",
    "AbstractTranslatableEntryBaseAdmin",
    "SeoEntryAdminMixin",
    "EntryAdmin",
)


# Ony register the admin when the entry model is not customized.
if get_entry_model() is Entry:
    admin.site.register(Entry, EntryAdmin)
