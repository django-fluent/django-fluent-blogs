from django.conf import settings
from django.template import Library

register = Library()

@register.tag
def blogurl(parser, token):
    """
    Compatibility tag to allow django-fluent-blogs to operate stand-alone.
    Either the app can be hooked in the URLconf directly, or it can be added as a pagetype of django-fluent-pages.
    For the former, URL resolving works via the normal '{% url "viewname" arg1 arg2 %}' syntax.
    For the latter, the URL resolving works via '{% appurl "viewname" arg1 arg2 %}' syntax.
    """
    if 'fluent_pages' in settings.INSTALLED_APPS:
        from fluent_pages.templatetags.appurl_tags import appurl
        return appurl(parser, token)
    else:
        # Using url from future, so the syntax is the same modern style.
        from django.templatetags.future import url
        return url(parser, token)
