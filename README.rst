Introduction
============


Installation
===========

First install the module, preferably in a virtual environment::

    mkvirtualenv fluent --no-site-packages
    workon fluent
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
        'fluent_contents',       # Optional but recommended.
        'django.contrib.comments',

        # The content plugins
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

To use the application stand alone, include the pages in ``urls.py``::

    urlpatterns += patterns('',
        url(r'^api/taggit_autocomplete_modified/', include('taggit_autocomplete_modified.urls')),
        url(r'^blog/comments/', include('django.contrib.comments.urls')),   # or fluent_comments.urls
        url(r'^blog/', include('fluent_blogs.urls')),
    )

Otherwise, don't include ``fluent_blogs.urls`` in the URLconf,
but add it as page type instead to django-fluent-pages::

    INSTALLED_APPS += (
        'fluent_pages',
        'fluent_blogs.pagetypes.blogpage',
    )

A "Blog" page can now be created in the page tree of *django-fluent-pages*.

The database can be created afterwards::

    ./manage.py syncdb
    ./manage.py runserver

