Introduction
============

This is a basic blogging engine, with the following features:

* Archive views by date, author, category and tags.
* Contents filled by django-fluent-contents_
* RSS and Atom feeds

Applications:

* Comments based on django.contrib.comments_ (can be styled with django-fluent-comments_ for example)
* Categories integrated with django-categories_
* *Optional* tagging with django-taggit_ and optionally django-taggit-autocomplete-modified_
* *Optional* integration with django-fluent-pages_
* *Optional* integration with django.contrib.sitemaps_

TODO:

* Provide a mechanism for custom fields, for example by using django-polymorphic_ for entries or a custom admin form.
* Have integration with publication protocols (like django-blog-zinnia_ provides), done in a similar way like django.contrib.syndication_ works.


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


Finishing up
------------

The database can be created afterwards::

    ./manage.py syncdb
    ./manage.py runserver


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

