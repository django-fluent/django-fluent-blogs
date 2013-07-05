Version 0.9.6
-------------

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
