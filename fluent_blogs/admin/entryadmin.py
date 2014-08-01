from django.contrib.admin import widgets
from fluent_blogs.admin.abstractbase import AbstractEntryBaseAdmin, AbstractTranslatableEntryBaseAdmin, SeoEntryAdminMixin
from fluent_blogs.models import get_entry_model, Entry_Translation
from parler.models import TranslatableModel


EntryModel = get_entry_model()

_model_fields = EntryModel._meta.get_all_field_names()
if issubclass(EntryModel, TranslatableModel):
    _entry_admin_base = AbstractTranslatableEntryBaseAdmin
    _model_fields += Entry_Translation.get_translated_fields()
else:
    _entry_admin_base = AbstractEntryBaseAdmin


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

    list_filter = list(_entry_admin_base.list_filter)
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

if 'categories' in _model_fields:
    EntryAdmin.list_filter.append('categories')
# This should only display tags that are in use, sorted by count:
#if 'tags' in _model_fields:
#    EntryAdmin.list_filter.append('tags')
