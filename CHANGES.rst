Version 0.9.2
-------------

* Fix initial south migrations, added missing dependencies.
* Fix automatic registration with django-fluent-comments_ and django-any-urlfield_ when not using custom models.


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
