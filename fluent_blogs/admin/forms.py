from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from parler.forms import TranslatableModelForm
from slug_preview.forms import SlugPreviewFormMixin

from fluent_blogs import appsettings
from fluent_blogs.models import get_entry_model
from fluent_blogs.models.query import get_date_range

EntryModel = get_entry_model()


class AbstractEntryBaseAdminForm(SlugPreviewFormMixin, ModelForm):
    """
    Base form for blog entries
    """

    def __init__(self, *args, **kwargs):
        super(AbstractEntryBaseAdminForm, self).__init__(*args, **kwargs)

        # The admin's .save() method fills in a default:
        self.fields['publication_date'].required = False
        try:
            author_field = self.fields['author']
        except KeyError:
            pass
        else:
            author_field.required = False
            self.initial.setdefault('author', author_field.user)

    def clean(self):
        cleaned_data = super(AbstractEntryBaseAdminForm, self).clean()
        if 'slug' not in cleaned_data or 'publication_date' not in cleaned_data:
            return cleaned_data

        try:
            self.validate_unique_slug(cleaned_data)
        except ValidationError as e:
            self._errors['slug'] = self.error_class(e.messages)

        return cleaned_data

    def clean_author(self):
        # Make sure the form never assigns None to the author value.
        return self.cleaned_data['author'] or self.fields['author'].user

    def validate_unique_slug(self, cleaned_data):
        """
        Test whether the slug is unique within a given time period.
        """
        date_kwargs = {}
        error_msg = _("The slug is not unique")

        # The /year/month/slug/ URL determines when a slug can be unique.
        pubdate = cleaned_data['publication_date'] or now()
        if '{year}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            date_kwargs['year'] = pubdate.year
            error_msg = _("The slug is not unique within it's publication year.")
        if '{month}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            date_kwargs['month'] = pubdate.month
            error_msg = _("The slug is not unique within it's publication month.")
        if '{day}' in appsettings.FLUENT_BLOGS_ENTRY_LINK_STYLE:
            date_kwargs['day'] = pubdate.day
            error_msg = _("The slug is not unique within it's publication day.")

        date_range = get_date_range(**date_kwargs)

        # Base filters are configurable for translation support.
        dup_filters = self.get_unique_slug_filters(cleaned_data)
        if date_range:
            dup_filters['publication_date__range'] = date_range

        dup_qs = EntryModel.objects.filter(**dup_filters)

        if self.instance and self.instance.pk:
            dup_qs = dup_qs.exclude(pk=self.instance.pk)

        # Test whether the slug is unique in the current month
        # Note: doesn't take changes to FLUENT_BLOGS_ENTRY_LINK_STYLE into account.
        if dup_qs.exists():
            raise ValidationError(error_msg)

    def get_unique_slug_filters(self, cleaned_data):
        # Allow to override this for translations
        return {
            'slug': cleaned_data['slug'],
        }


class AbstractTranslatableEntryBaseAdminForm(TranslatableModelForm, AbstractEntryBaseAdminForm):
    """
    Base form for translatable blog entries
    """

    def get_unique_slug_filters(self, cleaned_data):
        return {
            'translations__slug': cleaned_data['slug'],
            'translations__language_code': self.language_code
        }
