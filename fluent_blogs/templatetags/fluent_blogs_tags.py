from django.conf import settings
from django.template import Library, Node, TemplateSyntaxError
from django.template.loader import get_template
from fluent_blogs.models import Entry
from fluent_blogs.models.query import query_entries
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
    """
    return GetEntriesNode.parse(parser, token)



class GetEntriesNode(Node):
    model = Entry
    query_args = (
        'category', 'tag', 'author',
        'year', 'month', 'day',
        'orderby', 'order', 'limit',
    )


    def __init__(self, query, template_name, as_var):
        self.query_kwargs = query
        self.template_name = template_name
        self.as_var = as_var

        if template_name:
            template = get_template(template_name)
            self.nodelist = template.nodelist  # nodelist variable is special in 'Node' base class.
        else:
            self.nodelist = None


    @classmethod
    def parse(cls, parser, token):
        bits, as_var = parse_as_var(parser, token)
        arg_bits, kwarg_bits = parse_token_kwargs(parser, bits, True, True, ('template',) + cls.query_args)

        if len(arg_bits):
            raise TemplateSyntaxError("{0} tag only allows keyword arguments.".format(bits[0]))

        template_name = kwarg_bits.pop('template', None)
        return cls(
            query=kwarg_bits,
            template_name=template_name,
            as_var=as_var
        )


    def render(self, context):
        query_vars = dict((key, expr.resolve(context)) for key, expr in self.query_kwargs.iteritems())
        qs = self.model.objects.all()
        qs = query_entries(qs, **query_vars)

        if self.as_var:
            context[self.as_var] = qs
            return u''
        else:
            # render entry list using a template
            from django.template import Context
            context = Context()
            context.push()
            context['entries'] = qs
            output = self.nodelist.render(context)
            context.pop()
            return output
