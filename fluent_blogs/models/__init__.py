from django.conf import settings
from fluent_blogs.models.db import Entry

__all__ = ('Entry',)


def _register_url_type():
    from any_urlfield.models import AnyUrlField
    from any_urlfield.forms.widgets import SimpleRawIdWidget
    AnyUrlField.register_model(Entry, widget=SimpleRawIdWidget(Entry))


if 'any_urlfield' in settings.INSTALLED_APPS:
    _register_url_type()
