from django.template import Library
from fluent_blogs.admin import EntryAdmin

register = Library()

@register.simple_tag()
def status_column(entry):
    return EntryAdmin.get_status_column(entry)


@register.simple_tag()
def actions_column(entry):
    return EntryAdmin.get_actions_column(entry)
