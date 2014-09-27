from fluent_utils.softdeps.fluent_pages import mixed_reverse


def blog_reverse(viewname, args=None, kwargs=None, current_app='fluent_blogs', **page_kwargs):
    """
    Reverse a URL to the blog, taking various configuration options into account.

    This is a compatibility function to allow django-fluent-blogs to operate stand-alone.
    Either the app can be hooked in the URLconf directly, or it can be added as a pagetype of *django-fluent-pages*.
    """
    return mixed_reverse(viewname, args=args, kwargs=kwargs, current_app=current_app, **page_kwargs)


__all__ = (
    'blog_reverse',
)
