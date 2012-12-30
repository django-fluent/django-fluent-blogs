django-fluent-blogs
===================

This is a basic blogging engine, with the following features:

* Archive views by date, author, category and tags.
* Contents filled by django-fluent-contents_
* RSS and Atom feeds

Used applications:

* Comments based on django.contrib.comments_
* Categories based on django-categories_
* *Optional* integration with django-taggit_ and django-taggit-autocomplete-modified_ for tag support
* *Optional* integration with django-fluent-comments_ for Ajax-based comments
* *Optional* integration with django-fluent-pages_
* *Optional* integration with django.contrib.sitemaps_

TODO:

* Provide a mechanism for custom fields, for example by using django-polymorphic_ for entries or using a custom admin form.
* Have integration with blog publication protocols (like django-blog-zinnia_ provides), built in a similar way like django.contrib.syndication_ works.


Installation
============

First install the module, preferably in a virtual environment::

    git clone https://github.com/edoburu/django-fluent-blogs.git
    cd django-fluent-blogs
    pip install .

    # To add tagging support + autocomplete:
    pip install django-taggit django-taggit-autocomplete-modified


Configuration
-------------

Add the applications to ``settings.py``::

    INSTALLED_APPS += (
        # Blog engine + comments
        'fluent_blogs',
        'django.contrib.comments',

        # The content plugins
        'fluent_contents',
        'fluent_contents.plugins.text',

        # Support libs
        'categories',
        'categories.editor',
        'django_wysiwyg',

        # Optional tagging
        'taggit',
        'taggit_autocomplete_modified',
    )

    DJANGO_WYSIWYG_FLAVOR = "yui_advanced"

Note that not all applications are required;
tagging is optional, and so are the various ``fluent_contents`` plugins.

Include the apps in ``urls.py``::

    urlpatterns += patterns('',
        url(r'^admin/util/taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')),
        url(r'^blog/comments/', include('django.contrib.comments.urls')),
        url(r'^blog/', include('fluent_blogs.urls')),
    )

The database can be created afterwards:

    ./manage.py syncdb


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
* ``fluent_blogs/entry_detail/item.html``

These CSS/JavaScript includes are generated using:

* ``fluent_blogs/entry_detail/comments_css.html``
* ``fluent_blogs/entry_detail/comments_script.html``


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

