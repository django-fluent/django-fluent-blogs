import django
from django.core.urlresolvers import reverse
from django.template import Library
from django.utils.safestring import mark_safe

from fluent_blogs.admin import EntryAdmin
from fluent_blogs.models import get_entry_model

register = Library()


@register.simple_tag()
def status_column(entry):
    return mark_safe(EntryAdmin.get_status_column(entry))


@register.simple_tag()
def actions_column(entry):
    return mark_safe(EntryAdmin.get_actions_column(entry))


@register.simple_tag()
def blog_entry_admin_change_url(entry):
    model = get_entry_model()
    return reverse('admin:{0}_{1}_change'.format(model._meta.app_label, _get_meta_model_name(model._meta)), args=(entry.pk,))


# Despite using django-fluent-utils,
# this is only used here and fine as inline.
if django.VERSION >= (1, 6):
    def _get_meta_model_name(opts):
        return opts.model_name
else:
    def _get_meta_model_name(opts):
        return opts.module_name
