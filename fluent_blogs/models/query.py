from fluent_blogs.models.db import Entry

ORDER_BY_FIELDS = {
    'author': ('author__first_name', 'author__last_name'),
    'author_slug': ('author__username',),
    'category': ('categories__name',),
    'category_slug': ('categories__slug',),
    'tag': ('tags__name',),
    'tag_slug': ('tags__slug',),
    'date': ('publication_date',),
    'year': ('publication_date',),
}

ORDER_BY_DESC = ('date', 'year', 'month', 'day')


def query_entries(queryset=None,
        year=None, month=None, day=None,
        category=None, category_slug=None,
        tag=None, tag_slug=None,
        author=None, author_slug=None,
        future=False,
        order=None,
        orderby=None,
        limit=None,
    ):
    """
    Query the entries using a set of predefined filters.
    This interface is mainly used by the ``get_entries`` template tag.
    """
    if not queryset:
        queryset = Entry.objects.all()

    if not future:
        queryset = queryset.published()

    if year:
        queryset = queryset.filter(publication_date__year=year)
    if month:
        queryset = queryset.filter(publication_date__month=month)
    if day:
        queryset = queryset.filter(publication_date__day=day)

    # The main category/tag/author filters
    if category:
        if isinstance(category, basestring):
            queryset = queryset.filter(categories__slug=category)
        elif isinstance(category, (int, long)):
            queryset = queryset.filter(categories=category)
        else:
            raise ValueError("Expected slug or ID for the 'category' parameter")
    if category_slug:
        queryset = queryset.filter(categories__slug=category)

    if tag:
        if isinstance(tag, basestring):
            queryset = queryset.filter(tags__slug=tag)
        elif isinstance(tag, (int, long)):
            queryset = queryset.filter(tags=tag)
        else:
            raise ValueError("Expected slug or ID for 'tag' parameter.")
    if tag_slug:
        queryset = queryset.filter(tags__slug=tag)

    if author:
        if isinstance(author, basestring):
            queryset = queryset.filter(author__username=author)
        elif isinstance(author, (int, long)):
            queryset = queryset.filter(author=author)
        else:
            raise ValueError("Expected slug or ID for 'author' parameter.")
    if author_slug:
        queryset = queryset.filter(author__username=author_slug)


    # Ordering
    if orderby:
        try:
            db_fieldnames = ORDER_BY_FIELDS[orderby]
        except KeyError:
            raise ValueError("Invalid value for 'orderby', supported values are: {0}".format(', '.join(sorted(ORDER_BY_FIELDS.keys()))))

        if (not order and orderby in ORDER_BY_DESC) or (order or 'asc').lower() in ('desc', 'descending'):
            # Descending ordering by default for dates, or if requested.
            desc_fieldnames = map(lambda name: '-' + name, db_fieldnames)
            queryset = queryset.order_by(*desc_fieldnames)
        else:
            queryset = queryset.order_by(*db_fieldnames)

    # Limit
    if limit:
        queryset = queryset[:limit]

    return queryset
