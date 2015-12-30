Version 1.1 (2015-12-29)
------------------------

* Added Django 1.9 support.
* Added django-slug-preview_ for nicer slug appearance in the admin.
* Support translatable category names.
* Improved support for django-threadedcomments_.
* Using  django-categories-i18n_ as new default for the category model.


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
.. _django-fluent-comments: https://github.com/edoburu/django-fluent-comments
.. _django-fluent-contents: https://github.com/edoburu/django-fluent-contents
.. _django-fluent-pages: https://github.com/edoburu/django-fluent-pages
.. _django-categories-i18n: https://github.com/edoburu/django-categories-i18n
.. _django-parler: https://github.com/edoburu/django-parler
.. _django-slug-preview: https://github.com/edoburu/django-slug-preview
.. _django-taggit-autosuggest: https://bitbucket.org/fabian/django-taggit-autosuggest
.. _django-threadedcomments: https://github.com/HonzaKral/django-threadedcomments.git
