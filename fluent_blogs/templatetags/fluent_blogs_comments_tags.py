"""
A simple wrapper library, that makes sure that the template
``fluent_blogs/entry_detail/comments.html`` can still be rendered
when ``django_comments`` is not included in the site.

This way, project authors can easily use an online commenting system
(such as DISQUS or Facebook comments) instead.
"""
import warnings

from django.conf import settings
from django.template import Library
from django.utils.safestring import mark_safe
from fluent_utils.django_compat import is_installed

# Expose the tag library in the site.
# If `django_comments` is not used, this library can provide stubs instead.
# Currently, the real tags are exposed as the template already checks for `object.comments_are_open`.
# When a custom template is used, authors likely choose the desired commenting library instead.

if is_installed('threadedcomments') and getattr(settings, 'COMMENTS_APP', None):
    from threadedcomments.templatetags.threadedcomments_tags import register
elif is_installed('django_comments'):
    from django_comments.templatetags.comments import register
else:
    register = Library()

    @register.simple_tag
    def render_comment_list(for_, object):
        warnings.warn(
            "Can't render comments list: no comment app installed!\n"
            "Make sure either 'threadedcomments' and/or 'django_comments' is in INSTALLED_APPS"
        )
        return mark_safe("<!-- Can't render comments list: no comment plugin installed! -->")

    @register.simple_tag
    def render_comment_form(for_, object):
        warnings.warn(
            "Can't render comments form: no comment app installed!\n"
            "Make sure either 'threadedcomments' and/or 'django_comments' is in INSTALLED_APPS"
        )
        return mark_safe("<!-- no comment plugin installed! -->")
