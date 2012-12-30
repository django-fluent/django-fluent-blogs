Introduction
============

This is a basic blogging engine, with the following features:

* Archive views by date, author, category and tags.
* Contents filled by django-fluent-contents_
* RSS and Atom feeds

Applications:

* Comments based on django.contrib.comments_
* Categories based on django-categories_
* *Optional* integration with django-taggit_ and django-taggit-autocomplete-modified_ for tag support
* *Optional* integration with django-fluent-comments_ for Ajax-based comments
* *Optional* integration with django-fluent-pages_
* *Optional* integration with django.contrib.sitemaps_

TODO:

* Provide a mechanism for custom fields, for example by using django-polymorphic_ for entries or a custom admin form.
* Have integration with blog publication protocols (like django-blog-zinnia_ provides), done in a similar way like django.contrib.syndication_ works.


Installation
============

First install the module, preferably in a virtual environment::

    git clone https://github.com/edoburu/django-fluent-blogs.git
    cd django-fluent-blogs
    pip install .

Configuration
-------------

Next, create a project which uses the CMS::

    cd ..
    django-admin.py startproject fluentdemo

It should have the following settings::

    INSTALLED_APPS += (
        # Blog engine
        'fluent_blogs',

        # Comments system
        'fluent_comments',       # Optional but recommended.
        'django.contrib.comments',

        # The content plugins
        'fluent_contents',
        'fluent_contents.plugins.text',

        # Support libs
        'categories',
        'categories.editor',
        'django_wysiwyg',
        'mptt',

        # Optional tagging
        'taggit',
        'taggit_autocomplete_modified',

        # enable the admin
        'django.contrib.admin',
    )

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

Note some applications are optional.
The ``fluent_contents``, ``django.contrib.comments`` and ``categories`` are required.
Tagging is optional, and so are the various ``fluent_contents`` plugins.


Configuring the URLs
--------------------

To use the application stand alone, include the pages in ``urls.py``::

    urlpatterns += patterns('',
        url(r'^api/taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')),
        url(r'^blog/comments/', include('django.contrib.comments.urls')),   # or fluent_comments.urls
        url(r'^blog/', include('fluent_blogs.urls')),
    )

The application can also be used as pagetype in django-fluent-pages_.
In that case, don't include ``fluent_blogs.urls`` in the URLconf, but add it as page type instead::

    INSTALLED_APPS += (
        'fluent_pages',
        'fluent_blogs.pagetypes.blogpage',
    )

A "Blog" page can now be created in the page tree of django-fluent-pages_.

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

    {% block main %}{% block content %}{% endblock %}{% endblock %}

When all other block names are already available in the site's ``base.html`` template,
this example should be sufficient.

The filename of the base template can also be changed by defining the  ``FLUENT_BLOGS_BASE_TEMPLATE`` setting.

Comments
~~~~~~~~

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


Using other commenting systems
------------------------------

This module automatically integrates with django-fluent-comments_ when it's included in the ``INSTALLED_APPS``.
This will enable the moderation features, and include the required CSS and JavaScript files
that are needed to have a Ajax-based commenting system. These tags are generated using:

* ``fluent_blogs/entry_detail/comments_css.html``
* ``fluent_blogs/entry_detail/comments_script.html``

To use a different commenting system instead of django.contrib.comments_ (e.g. Facebook-comments_ or DISQUS_), override the following templates:

* ``fluent_blogs/entry_detail/comments.html``
* ``fluent_blogs/entry_detail/item.html``


Finishing up
------------

The database can be created afterwards::

    ./manage.py syncdb
    ./manage.py runserver


.. _DISQUS: http://disqus.com/
.. _django-blog-zinnia: http://django-blog-zinnia.com/documentation/
.. _django.contrib.syndication: https://docs.djangoproject.com/en/dev/ref/contrib/syndication/
.. _django.contrib.comments: https://docs.djangoproject.com/en/dev/ref/contrib/comments/
.. _django.contrib.sitemaps: https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/
.. _django-categories: https://github.com/callowayproject/django-categories
.. _django-fluent-comments: https://github.com/edoburu/django-fluent-comments
.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
.. _django-fluent-pages: https://github.com/edoburu/django-fluent-pages
.. _django-polymorphic: https://github.com/bconstantin/django_polymorphic
.. _django-taggit: https://github.com/alex/django-taggit
.. _django-taggit-autocomplete-modified: http://packages.python.org/django-taggit-autocomplete-modified/
.. _Facebook-comments: https://developers.facebook.com/docs/reference/plugins/comments/

