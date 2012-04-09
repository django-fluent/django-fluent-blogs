from django.conf import settings
from django.core.urlresolvers import reverse

_HAS_FLUENT_PAGES = ('fluent_pages' in settings.INSTALLED_APPS)
if _HAS_FLUENT_PAGES:
    from fluent_pages.urlresolvers import mixed_reverse


def blog_reverse(viewname, args=None, kwargs=None, current_app='fluent_blogs', current_page=None, multiple=False, ignore_multiple=False):
    """
    Reverse a URL to the blog, taking various configuration options into account.

    This is a compatibility function to allow django-fluent-blogs to operate stand-alone.
    Either the app can be hooked in the URLconf directly, or it can be added as a pagetype of *django-fluent-pages*.
    """
    if _HAS_FLUENT_PAGES:
        return mixed_reverse(viewname, args=args, kwargs=kwargs, current_page=current_page, multiple=multiple, ignore_multiple=ignore_multiple)
    else:
        return reverse(viewname, args=args, kwargs=kwargs, current_app=current_app)


__all__ = (
    'blog_reverse',
)
