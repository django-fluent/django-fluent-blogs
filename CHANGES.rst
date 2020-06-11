Version 2.0.6 (2020-06-11)
--------------------------

* Added a "hidden" status to hide blog entries in the archive listings.
  This makes the entries only accessible through a direct link.
* Added ``BlogPage.get_entry_queryset()``, which allows limiting the entries shown at a particular ``BlogPage``.


Version 2.0.5 (2020-01-04)
--------------------------

* Fixed Django 3.0 compatibility by removing ``django.utils.six`` dependency.
* Fixed ``{% static .. %}`` usage in templates.
* Bumped dependencies to Django 3.0 compatible versions.


Version 2.0.4 (2019-07-15)
--------------------------

* Fixed ``manage.py migrate_blog_categories`` command for modern Django.
* Fix Python 3 issue with ``query_entries()`` / ``{% get_entries category='..' %}``.
* Reorder admin fieldsets to match django-fluent-pages_.
* Reformatted all files with isort and black.


Version 2.0.3 (2018-07-31)
--------------------------

* Added ``FLUENT_BLOGS_PAGINATE_BY`` setting.
* Enforce newer django-slug-preview_ and django-fluent-contents_ for proper Django 2.0 support


Version 2.0.2 (2018-02-12)
--------------------------

* Added support for custom user model / username fields on Django 1.11+
* Fix duplicate tag pages in the sitemap
* Fix HTML display in admin list columns for Django 2.0


Version 2.0.1 (2018-02-05)
--------------------------

* Added missing migration for the new ``on_delete=SET_NULL`` behavior for the author field.


Version 2.0 (2018-01-22)
------------------------

* Added Django 2.0 support.
* Fixed support for django-polymorphic_ 2.0.
* Fixed ``og:type`` for blog articles, to return ``article``.
* Dropped Django 1.8 and 1.9 support.


Version 1.3 (2017-08-04)
------------------------

* Dropped Django 1.6 and 1.7 support.
* Fix migrations being regenerated on Python 3 due to str/bytes differences.
* Fix Django 1.10 invocation of management commands
* Fix ``FluentContentsPage`` import to use the proper new location.


Version 1.2.4 (2017-02-03)
--------------------------

* Added ``tags`` and ``categories`` blocks to the ``fluent_blogs/entry_contents_base.html`` template
* Fixed duplicate query count for categories and tags.
* Fixed minor Python 3 issue with error handling of ``FeedView``
* Fixed Python 3 ``__str__()`` for blog models
* Using django-tag-parser_ 3.0


Version 1.2.3 (2016-06-19)
--------------------------

* Fixed possible ``PageTypeNotMounted`` error on slug preview URL field.
* Fixed Django version testing in ``get_entry_model()``.
* Fixed translated page URLs when the ``BlogPage`` root does not have a fallback yet.
* Fixed date checking for detail page URL.
* Fixed Django 1.9 issue with ``{% blogurl .. %}`` tag.


Version 1.2.2 (2016-05-17)
--------------------------

* Fixed previewing blog enties for staff members.
* Fixed the category RSS feeds when using django-categories-i18n_.
* Enhanced the template inheritance, to make sure language tabs are always shown.
  Custom blog admin classes can now redefine ``change_form_template`` without getting issues.


Version 1.2.1 (2016-03-21)
--------------------------

* Fixed default ordering of entries in the archive listings.
* Fixed Django 1.9 warnings for ``get_all_field_names()``
* Fixed ``manage.py migrate_blog_categories`` usage warning for older Django versions.
* Added ``{% block og-image %}`` block to the default templates.


Version 1.2 (2016-02-07)
------------------------

* Added support for ``{% page_placeholder %}`` in the blog archive templates.
  This allows defining a sidebar of 'intro' area in a blog page using placeholders.
  Previously, this was only possible by adding a ``{% shared_content "blog_sidebar" %}`` tag in the template.
* Added ``fluent_blogs.base_models.ExcerptTextEntryMixin`` and ``fluent_blogs.base_models.ExcerptImageEntryMixin`` for easy excerpt support.
* **BACKWARDS INCOMPATIBLE:** Deprecated the old 'intro' field, it's hidden from the admin now.
  Consider creating a custom model/admin with the excerpt mixins instead.
  The field is kept in the model to avoid data-loss. If you want to restore it in the admin,
  add the following to your settings file::

      FLUENT_BLOGS_EXTRA_ADMIN_FIELDS = ('intro',)

  or override the blog model and admin.

* Moved ``fluent_blogs.models.manages`` to ``fluent_blogs.managers`` to avoid circular import errors when working with custom models.
  The old import location still works, but will raise a ``DeprecationWarning``.
* Fixed appearance of list icons in Django 1.9.
* Fixed rendering empty pages instead of using the fallback language.
* **NOTE:** If you manually included ``{% wysiwyg_editor "excerpt_text" %}`` in the admin ``change_form.html`` page,
  please remove it. It will be initialized automatically with a WYSIWYG editor now.


Version 1.1.2 (2016-01-04)
--------------------------

* Fixed RSS feeds when using django-categories-i18n


Version 1.1.1 (2015-12-31)
--------------------------

* Fixed admin list view for blog entries.
* Added ``migrate_blog_categories`` command to replace the Blog category model, and update foreign keys.


Version 1.1 (2015-12-30)
------------------------

* Added Django 1.9 support.
* Added django-slug-preview_ for nicer slug appearance in the admin.
* Support translatable category names.
* Improved support for django-threadedcomments_.
* Using  django-categories-i18n_ as new default for the category model.
* Dropped Django 1.4 support.


Version 1.0.2 (2015-11-17)
--------------------------

* Added stub ``% render_comment_list %]`` / ``{% render_comment_form %}`` template tags in case no comments app is installed.
* Added more fields in the default ``list_filter``.
* Fix the ``EntryAdmin`` to fully support custom models in the ``fieldsets``.
* Fix the ``EntryAdmin`` to use ``fieldsets`` instead of ``declared_fieldsets``.
* Fix ``fullheadtitle`` => ``meta-title`` template block name.
* Fix import errors with ``get_entry_model()``.


Version 1.0.1 (2015-08-19)
--------------------------

* Fix having a mandatory ``SITE_ID`` setting.
* Fix ``DeprecationWarning`` for using ``placeholder_tags`` instead of ``fluent_contents_tags`` in RSS feed.
* Small stylefix for *django-suit*


Version 1.0
-----------

* Added Django 1.7/1.8 compatibility
* Fixed ``{% get_tags %}`` for Django 1.6.
* Fixed using ``publication_date`` instead of ``creation_date`` in the templates.
* Added ``Entry.create_placeholder()`` API function.


Released in 1.0b4:
~~~~~~~~~~~~~~~~~~

* Fixed check for django-fluent-contents_ some python versions.


Released in 1.0b3:
~~~~~~~~~~~~~~~~~~

* Added Django 1.7 support.
* Add "fluent_blogs_archive_index.html" template for the index view.
* Add SEO keywords/description/title fields to the ``BlogPage`` root.
* Admin: show categories in the list.


Released in 1.0b2:
~~~~~~~~~~~~~~~~~~

* Added support for django-taggit-autosuggest_.
* Fixed entry URLs to be relative to the current ``BlogPage`` root.
* Fixed next/previous URLs for translated content (in case the next URL only exists in certain languages).
* Include editable author field in the "Publication settings" tab.


Released in 1.0b1:
~~~~~~~~~~~~~~~~~~

* Added multisite support.
* Added optional multilingual support, based on django-parler_.
* Added meta keywords/description fields.
* Added new base templates to make overriding ``entry_archive.html`` and ``entry_details.html`` easier.
* Added abstract base classes for multilingual support.
* Added ``blog-entry-wrapper`` and ``blog-archive-wrapper`` classes in the template
* Allow ``formfield_overrides`` to contain field names too.
* Fix comments-stub support for Django 1.6
* Fix ``get_tags`` template tag to returns tags for unpublished entries only.
* Fix ``get_tags`` template tag to handle multple ``BlogPage`` instances.


Version 0.9.7
-------------

* Fix a circular import in ``base_models.py`` which happened with ``DEBUG = False`` only.
* Fixed missing ``block.super`` call for the ``link`` template block.


Version 0.9.6
-------------

* Fix empty admin edit screen when using custom models.
* Fix year formatting in the year archive pages (e.g. ``/blog/2013/``) when using Django 1.5 and up.


Version 0.9.5
-------------

* Add ``FLUENT_BLOGS_INCLUDE_STATIC_FILES`` setting, to disable automatic inclusion the CSS/JS files of django-fluent-comments_.


Version 0.9.4
-------------

* Support using the same slug in different months.


Version 0.9.3
-------------

* Improve error message when a blogmodule is not yet attached to the django-fluent-pages_ page tree.
* Fix the blog ordering at the "Blog page" edit screen.
* Fix running the code at Django 1.6
* Fix 500 error feed view
* Marked ``AbstractEntryBaseAdminForm`` and ``EntryManager`` as public classes


Version 0.9.2
-------------

* Fix initial south migrations, added missing dependencies.
* Fix automatic registration with django-fluent-comments_ and django-any-urlfield_ when not using custom models.
* Fix comments count indicator, ``CommentsEntryMixin.comments`` also ignores removed comments now.


Version 0.9.1
-------------

* Fix url reference to Entry model when using custom models


Version 0.9.0
-------------

First PyPI release.

Reached a mature point where a release can be made.
Main features:

* Archive views by date, author, category and tags.
* Contents filled by django-fluent-contents_
* RSS and Atom feeds
* Granularity in templates to override layouts.
* Abstract base model for custom blog models.

.. _django-any-urlfield: https://github.com/edoburu/django-any-urlfield
.. _django-fluent-comments: https://github.com/django-fluent/django-fluent-comments
.. _django-fluent-contents: https://github.com/django-fluent/django-fluent-contents
.. _django-fluent-pages: https://github.com/edoburu/django-fluent-pages
.. _django-categories-i18n: https://github.com/edoburu/django-categories-i18n
.. _django-parler: https://github.com/django-parler/django-parler
.. _django-slug-preview: https://github.com/edoburu/django-slug-preview
.. _django-tag-parser: https://github.com/edoburu/django-tag-parser
.. _django-taggit-autosuggest: https://bitbucket.org/fabian/django-taggit-autosuggest
.. _django-threadedcomments: https://github.com/HonzaKral/django-threadedcomments.git
