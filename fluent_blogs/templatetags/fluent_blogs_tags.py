from django.conf import settings
from django.template import Library, Node, Context, TemplateSyntaxError
from django.template.loader import get_template
from fluent_blogs.models import Entry
from fluent_blogs.models.query import query_entries, query_tags
from fluent_blogs.utils.tagparsing import parse_token_kwargs, parse_as_var

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


class AssignmentOrInclusionNode(Node):
    """
    Base class to either assign a tag, or render it using a template.
    """
    allowed_kwargs = ()
    context_object_name = 'object'


    def __init__(self, template_name, as_var, **kwargs):
        self.template_name = template_name
        self.as_var = as_var
        self.kwargs = kwargs

        if template_name:
            template = get_template(template_name)
            self.nodelist = template.nodelist  # nodelist variable is special in 'Node' base class.
        else:
            self.nodelist = None


    @classmethod
    def parse(cls, parser, token):
        bits, as_var = parse_as_var(parser, token)
        arg_bits, kwarg_bits = parse_token_kwargs(parser, bits, True, True, ('template',) + cls.allowed_kwargs)

        if len(arg_bits):
            raise TemplateSyntaxError("{0} tag only allows keyword arguments.".format(bits[0]))

        template_name = kwarg_bits.pop('template', None)
        return cls(
            template_name=template_name,
            as_var=as_var,
            **kwarg_bits
        )


    def render(self, context):
        vars = dict((key, expr.resolve(context)) for key, expr in self.kwargs.iteritems())
        object_data = self.get_object_data(**vars)

        if self.as_var:
            context[self.as_var] = object_data
            return u''
        else:
            # render entry list using a template
            context = Context()
            context.push()
            context[self.context_object_name] = object_data
            output = self.nodelist.render(context)
            context.pop()
            return output

    def get_object_data(self, **kwargs):
        raise NotImplementedError("The '{0}' subclass needs to implement 'get_object_data'.".format(self.__class__.__name__))



@register.tag
def get_entries(parser, token):
    """
    Query the entries in the database, and render them.
    This template tag supports the following syntax:

    .. code-block:: html+django

        {% get_entries category='slug' year=2012 as entries %}
        {% for entry in entries %}...{% endfor

        {% get_entries category='slug' year=2012 template="name/of/template.html" %}

    The allowed query parameters are:

    * ``category``: The slug or ID of a category
    * ``tag``: The slug or ID of a tag
    * ``author``: The username or ID of an author
    * ``year``: The full year.
    * ``month``: The month number to display
    * ``day``: The day of the month to display.
    * ``order``: Which field to order on, this can be:
    
     * ``slug``: The URL name of the entry.
     * ``title``: The title of the entry.
     * ``author``: The author full name
     * ``author_slug``: The author URL name.
     * ``category``: The category name.
     * ``category_slug``: The category URL name.
     * ``tag``: The tag name
     * ``tag_slug``: The tag URL name.
     * ``date``: The publication date of the entry.

    * ``orderby``: can be ASC/ascending or DESC/descending. The default depends on the ``order`` field.
    * ``limit``: The maximum number of entries to return.
    """
    return GetEntriesNode.parse(parser, token)



class GetEntriesNode(AssignmentOrInclusionNode):
    context_object_name = 'entries'
    allowed_kwargs = (
        'category', 'tag', 'author',
        'year', 'month', 'day',
        'orderby', 'order', 'limit',
    )
    model = Entry

    def get_object_data(self, **query_vars):
        # Query happens in the backend,
        # the templatetag is considered to be a frontend.
        qs = self.model.objects.all()
        qs = query_entries(qs, **query_vars)
        return qs



@register.tag
def get_tags(parser, token):
    """
    Find the popular tags associated with blog entries.
    This template tag supports the following syntax:

    .. code-block:: html+django

        {% get_popular_tags order="name" as tags %}
        {% for tag in tags %}...{% endfor %}

        {% get_popular_tags template="name/of/template.html" %}

    The allowed query parameters are:

    * ``order``: Which field to order on, this can be:

     * ``slug``: The URL name of the tag.
     * ``name``: The name of the tag.
     * ``count``: The number of times the tag is used.

    * ``orderby``: can be ASC/ascending or DESC/descending. The default depends on the ``order`` field.
    * ``limit``: The maximum number of entries to return.

    The returned :class:`~taggit.models.Tag` objects have a ``count`` attribute attached
    with the amount of times the tag is used.
    """
    return GetPopularTagsNode.parse(parser, token)



class GetPopularTagsNode(AssignmentOrInclusionNode):
    context_object_name = 'tags'
    allowed_kwargs = (
        'order', 'orderby', 'limit',
    )

    def get_object_data(self, **kwargs):
        return query_tags(**kwargs)
