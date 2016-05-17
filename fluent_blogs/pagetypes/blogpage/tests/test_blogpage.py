import django

from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import set_urlconf, get_urlconf
from django.test import TestCase
from django.utils import translation

from fluent_blogs.models import Entry
from fluent_blogs.pagetypes.blogpage.models import BlogPage
from fluent_pages.urlresolvers import PageTypeNotMounted


class BlogPageTests(TestCase):
    """
    Testing integration between django-fluent-pages and django-fluent-blogs
    """

    @classmethod
    def setUpClass(cls):
        super(BlogPageTests, cls).setUpClass()

        User = get_user_model()

        Site.objects.get_or_create(id=settings.SITE_ID, defaults=dict(domain='django.localhost', name='django at localhost'))
        cls.user = User.objects.create_superuser("fluent-blogs-admin", 'admin@example.org', 'admin')

        # Testing with other URLconf, this works for every Django version
        cls._old_urlconf = get_urlconf()
        set_urlconf('fluent_blogs.pagetypes.blogpage.tests.urls')

    @classmethod
    def tearDownClass(cls):
        super(BlogPageTests, cls).tearDownClass()
        set_urlconf(cls._old_urlconf)

    def tearDown(self):
        cache.clear()  # BlogPage URLs are stored in cache

    def test_no_blogpage(self):
        date = datetime(year=2016, month=5, day=1)
        entry = Entry.objects.language('en').create(author=self.user, slug='foo', publication_date=date)
        self.assertRaises(PageTypeNotMounted, lambda: entry.default_url)

    def test_blogpage_fallback_url(self):
        """
        Testing how translated entries appear on a ``BlogPage`` that has no translation except for the default/fallback.
        """
        page = BlogPage.objects.language('en').create(author=self.user, status=BlogPage.PUBLISHED, slug='blog')
        self.assertEqual(page.default_url, '/en/blog/')

        date = datetime(year=2016, month=5, day=1)
        entry = Entry.objects.language('en').create(author=self.user, slug='hello-en', publication_date=date)
        self.assertEqual(entry.default_url, '/en/blog/2016/05/hello-en/')

        # Simulate fetched entry in new language
        with translation.override('nl'):
            entry.set_current_language('nl')
            self.assertEqual(entry.default_url, '/nl/blog/2016/05/hello-en/')

            # Create new language
            entry.create_translation('nl', slug='hello-nl')
            self.assertEqual(entry.default_url, '/nl/blog/2016/05/hello-nl/')
