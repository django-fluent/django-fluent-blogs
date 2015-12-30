django-fluent-blogs
===================

This is a basic blogging engine, with the following features:

* Archive views by date, author, category and tags.
* Contents filled by django-fluent-contents_
* RSS and Atom feeds
* Granularity in templates to override layouts.
* Abstract base model for custom blog models.

Used applications:

* Categories based on django-categories-i18n_ (or django-categories_).
* *Optional* comments based on django.contrib.comments_
* *Optional* multilingual support based on django-parler_.
* *Optional* integration with django-taggit_ and django-taggit-autocomplete-modified_ for tag support
* *Optional* integration with django-fluent-comments_ for Ajax-based comments
* *Optional* integration with django-fluent-pages_
* *Optional* integration with django.contrib.sitemaps_

TODO:

* Have integration with blog publication protocols (like django-blog-zinnia_ provides), built in a similar way like django.contrib.syndication_ works.


Installation
============

First install the module, preferably in a virtual environment::

    git clone https://github.com/edoburu/django-fluent-blogs.git
    cd django-fluent-blogs
    pip install .

    # Install the plugins of fluent-contents that you use:
    pip install django-fluent-contents[text]

    # Optional: to add tagging support + autocomplete use:
    pip install django-taggit django-taggit-autocomplete-modified


Configuration
-------------

Add the applications to ``settings.py``::

    INSTALLED_APPS += (
        # Blog engine
        'fluent_blogs',

        # The content plugins
        'fluent_contents',
        'fluent_contents.plugins.text',

        # Support libs
        'categories_i18n',
        'django_wysiwyg',
        'slug_preview',

        # Optional commenting support
        'django.contrib.comments',

        # Optional tagging
        'taggit',
        'taggit_autocomplete_modified',
    )

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

Note that not all applications are required;
tagging is optional, and so are the various ``fluent_contents.plugin.*`` packages.

Include the apps in ``urls.py``::

    urlpatterns += patterns('',
        url(r'^admin/util/taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')),
        url(r'^blog/comments/', include('django.contrib.comments.urls')),
        url(r'^blog/', include('fluent_blogs.urls')),
    )

The database can be created afterwards::

    ./manage.py syncdb

In case additional plugins of django-fluent-contents_ are used, follow their
`installation instructions <http://django-fluent-contents.readthedocs.org/en/latest/plugins/index.html>`_ as well.
Typically this includes:

* adding the package name to ``INSTALLED_APPS``.
* running ``pip install django-fluent-contents[pluginname]``
* running  ``./manage.py syncdb``


Configuring the templates
-------------------------

To display the blog contents, a ``fluent_blogs/base.html`` file needs to be created.
This will be used to map the output of the module to your site templates.

The base template needs to have the blocks:

* ``content`` - displays the main content
* ``title`` - the ``<head>`` title fragment.
* ``link`` - displays ``<link>`` tags for RSS feeds.
* ``script`` - includes additional ``<script>`` tags.
* ``meta-description`` - the ``value`` of the meta-description tag.
* ``meta-keywords`` - the ``value`` for the meta-keywords tag.
* ``og-type`` - the OpenGraph type for Facebook (optional)
* ``og-description`` the OpenGraph description for Facebook (optional)

The ``fluent_blogs/base.html`` template could simply remap the block names to the site's ``base.html`` template.
For example::

    {% extends "base.html" %}

    {% block headtitle %}{% block title %}{% endblock %}{% endblock %}

    {% block main %}
        {# This area is filled with the blog archive/details:
        {% block content %}{% endblock %}

        {# Add any common layout, e.g. a sidebar here #}
    {% endblock %}

When all other block names are already available in the site's ``base.html`` template,
this example should be sufficient.

The filename of the base template can also be changed by defining the  ``FLUENT_BLOGS_BASE_TEMPLATE`` setting.

Comments
~~~~~~~~

The commenting support can be based on django.contrib.comments_, or any other system of your choice.
To integrate django.contrib.comments_ with your site theme, also create a ``comments/base.html`` template that maps the blocks:

* ``title``
* ``content``
* ``extrahead`` (only for django-fluent-comments_)


Adding pages to the sitemap
---------------------------

Optionally, the blog pages can be included in the sitemap.
Add the following in ``urls.py``::

    from fluent_blogs.sitemaps import EntrySitemap, CategoryArchiveSitemap, AuthorArchiveSitemap, TagArchiveSitemap

    sitemaps = {
        'blog_entries': EntrySitemap,
        'blog_categories': CategoryArchiveSitemap,
        'blog_authors': AuthorArchiveSitemap,
        'blog_tags': TagArchiveSitemap,
    }

    urlpatterns += patterns('',
        url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    )


Integration with django-fluent-pages:
-------------------------------------

To integrate with the page types of django-fluent-pages_, don't include ``fluent_blogs.urls`` in the URLconf::

    urlpatterns += patterns('',
        url(r'^admin/util/taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')),
        url(r'^blog/comments/', include('django.contrib.comments.urls')),   # or fluent_comments.urls
    )

Instead, add a page type instead::

    INSTALLED_APPS += (
        'fluent_pages',
        'fluent_blogs.pagetypes.blogpage',
    )

A "Blog" page can now be created in the page tree of django-fluent-pages_
at the desired URL path.


Integration with django-fluent-comments:
----------------------------------------

To use Ajax-based commenting features of django-fluent-comments_, include it in ``settings.py``::

    INSTALLED_APPS += (
        'fluent_blogs',
        'fluent_comments',      # Before django.contrib.comments
        'django.contrib.comments',

        ...
    )

Include the proper module in ``urls.py``::

    urlpatterns += patterns('',
        url(r'^blog/comments/', include('fluent_comments.urls')),

        ...
    )

This module will detect the installation, and enable the moderation features and include
the required CSS and JavaScript files to have a Ajax-based commenting system.


Integration with other commenting systems
-----------------------------------------

To use a different commenting system instead of django.contrib.comments_ (e.g. DISQUS_ or Facebook-comments_), override the following templates:

* ``fluent_blogs/entry_detail/comments.html``

These CSS/JavaScript includes are generated using:

* ``fluent_blogs/entry_detail/comments_css.html``
* ``fluent_blogs/entry_detail/comments_script.html``


Overriding the blog layout
--------------------------

To change the layout of the blog , the following templates can be overwritten:

In the archive/list page:

* ``fluent_blogs/entry_archive.html`` - the starting point, which includes all sub templates:
* ``fluent_blogs/entry_archive/item.html`` - a single list item (extends ``fluent_blogs/entry_contents_base.html``).
* ``fluent_blogs/entry_archive/empty.html`` - the default message when there are no entries.
* ``fluent_blogs/entry_archive/pagination.html`` - the pagination at the bottom of the page.

In the detail page:

* ``fluent_blogs/entry_detail.html`` - the starting point, which includes all sub templates:
* ``fluent_blogs/entry_detail/contents.html`` - the entry contents (extends ``fluent_blogs/entry_contents_base.html``).
* ``fluent_blogs/entry_detail/widgets.html`` - space to add Social Media buttons.
* ``fluent_blogs/entry_detail/comments.html`` - the comments.
* ``fluent_blogs/entry_detail/navigation.html`` - the entry navigation links
* ``fluent_blogs/entry_detail/page_footer.html`` - space below the comments to add Social Media buttons.
* ``fluent_blogs/entry_detail/comments_css.html``
* ``fluent_blogs/entry_detail/comments_script.html``

Common appearance:

* ``fluent_blogs/entry_contents_base.html`` - the common appearance of entries in the archive and detail page.
* ``fluent_blogs/base.html`` - the base template, e.g. to introduce a common sidebar.


Shared entry layout
~~~~~~~~~~~~~~~~~~~

When the layout of individual entries is shared with

* By default, the contents ``fluent_blogs/entry_archive/item.html`` and , based on ``fluent_blogs/entry_archive/item.html`` by default


Custom entry models
-------------------

This applications supports the use of custom models for the blog entries.
Include the following setting in your project::

    FLUENT_BLOGS_ENTRY_MODEL = 'myapp.ModelName'

This application will use the custom model for feeds, views and the sitemap.
The model can either inherit from the following classes:

* ``fluent_blogs.models.Entry`` (the default entry)
* ``fluent_blogs.base_models.AbstractEntry`` (the default entry, as abstract model)
* A mix of ``fluent_blogs.base_models.AbstractEntryBase`` combined with:

 * ``fluent_blogs.base_models.ExcerptEntryMixin``
 * ``fluent_blogs.base_models.ContentsEntryMixin``
 * ``fluent_blogs.base_models.CommentsEntryMixin``
 * ``fluent_blogs.base_models.CategoriesEntryMixin``
 * ``fluent_blogs.base_models.TagsEntryMixin``

When a custom model is used, the admin needs to be registered manually.
The admin can inherit from either:

* ``fluent_blogs.admin.AbstractEntryBaseAdmin``
* ``fluent_blogs.admin.EntryAdmin``

The views are still rendered using the same templates, but you can also override:

* ``myapp/modelname_archive_*.html``
* ``myapp/modelname_detail.html``
* ``myapp/modelname_feed_description.html``


Contributing
------------

This module is designed to be generic, and easy to plug into your site.
In case there is anything you didn't like about it, or think it's not
flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)



.. _DISQUS: http://disqus.com/
.. _django-blog-zinnia: http://django-blog-zinnia.com/documentation/
.. _django.contrib.syndication: https://docs.djangoproject.com/en/dev/ref/contrib/syndication/
.. _django.contrib.comments: https://docs.djangoproject.com/en/dev/ref/contrib/comments/
.. _django.contrib.sitemaps: https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/
.. _django-categories: https://github.com/callowayproject/django-categories
.. _django-categories-i18n: https://github.com/edoburu/django-categories-i18n
.. _django-fluent-comments: https://github.com/edoburu/django-fluent-comments
.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
.. _django-fluent-pages: https://github.com/edoburu/django-fluent-pages
.. _django-parler: https://github.com/edoburu/django-parler
.. _django-polymorphic: https://github.com/bconstantin/django_polymorphic
.. _django-taggit: https://github.com/alex/django-taggit
.. _django-taggit-autocomplete-modified: http://packages.python.org/django-taggit-autocomplete-modified/
.. _Facebook-comments: https://developers.facebook.com/docs/reference/plugins/comments/

