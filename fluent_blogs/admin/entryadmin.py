from django.conf import settings
from django.contrib.admin import widgets
from parler.models import TranslatableModel

from fluent_blogs import appsettings
from fluent_blogs.admin.abstractbase import (
    AbstractEntryBaseAdmin,
    AbstractTranslatableEntryBaseAdmin,
    SeoEntryAdminMixin,
)
from fluent_blogs.models import get_entry_model

EntryModel = get_entry_model()
_model_fields = [f.name for f in EntryModel._meta.get_fields()]

if issubclass(EntryModel, TranslatableModel):
    _entry_admin_base = AbstractTranslatableEntryBaseAdmin
    # Some of the mixin fields could appear in the translated model instead of the regular shared model.
    # Add those fields here, so they will be added to the fieldsets by default as well.
    _model_fields += EntryModel._parler_meta.get_all_fields()
    _is_translated = True
else:
    _entry_admin_base = AbstractEntryBaseAdmin
    _is_translated = False


class EntryAdmin(SeoEntryAdminMixin, _entry_admin_base):
    """
    The Django admin class for the blog model.
    When another blog model is used, the ``fieldsets`` include it's additional fields.
    You can also use :class:`AbstractEntryBaseAdmin` with an optional ``SeoEntryAdminMixin``,
    to control the admin field layout completley.
    """

    # Redefine the fieldset, because it will be extended with auto-detected fields.
    FIELDSET_GENERAL = (
        None,
        {
            "fields": (
                "title",
                "slug",
                "status",
            ),  # is filled with ('contents', 'categories', 'tags', 'enable_comments') below
        },
    )

    if "meta_keywords" in _model_fields:
        fieldsets = [
            FIELDSET_GENERAL,
            SeoEntryAdminMixin.FIELDSET_SEO,
            AbstractEntryBaseAdmin.FIELDSET_PUBLICATION,
        ]
    else:
        fieldsets = [
            FIELDSET_GENERAL,
            AbstractEntryBaseAdmin.FIELDSET_PUBLICATION,
        ]

    list_filter = ["status"]  # reset, is rebuilt below.
    html_fields = []  # auto filled with excerpt_text
    formfield_overrides = {}
    formfield_overrides.update(SeoEntryAdminMixin.formfield_overrides)
    formfield_overrides.update(
        {
            "intro": {"widget": widgets.AdminTextareaWidget(attrs={"rows": 4})},
        }
    )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["html_fields"] = self.html_fields
        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["html_fields"] = self.html_fields
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context
        )


# Add all optional mixin fields
for _f in appsettings.FLUENT_BLOGS_ADMIN_FIELDS:
    if _f in _model_fields:
        EntryAdmin.FIELDSET_GENERAL[1]["fields"] += (_f,)

# Add filters for optional mixin fields
# Note, not adding 'tags' yet. It should only display tags that are in use, sorted by count.
if "categories" in _model_fields:
    EntryAdmin.list_filter.append("categories")
if _is_translated and getattr(settings, "PARLER_LANGUAGES", None):
    EntryAdmin.list_filter.append("translations__language_code")
if "enable_comments" in _model_fields:
    EntryAdmin.list_filter.append("enable_comments")

# Autodetect HTML fields of known built-in mixins
if "excerpt_text" in _model_fields:
    EntryAdmin.html_fields.append("excerpt_text")
