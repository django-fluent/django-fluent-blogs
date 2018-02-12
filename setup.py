#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import codecs
import os
import re
import sys


# When creating the sdist, make sure the django.mo file also exists:
if 'sdist' in sys.argv or 'develop' in sys.argv:
    os.chdir('fluent_blogs')
    try:
        from django.core import management
        management.call_command('compilemessages', stdout=sys.stderr, verbosity=1)
    except ImportError:
        if 'sdist' in sys.argv:
            raise
    finally:
        os.chdir('..')


def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


setup(
    name='django-fluent-blogs',
    version=find_version('fluent_blogs', '__init__.py'),
    license='Apache 2.0',

    install_requires=[
        'django-fluent-contents>=2.0.2',
        'django-fluent-utils>=2.0',
        'django-categories-i18n>=1.1',
        'django-parler>=1.9.1',
        'django-slug-preview>=1.0.4',
        'django-tag-parser>=3.1',
    ],
    requires=[
        'Django (>=1.10)',
    ],
    extras_require = {
        'tests': [
            'django-fluent-pages>=2.0.1',
            'django-wysiwyg>=0.7.1',
        ],
        'blogpage': ['django-fluent-pages>=2.0.1'],
        'taggit': ['taggit', 'taggit-autosuggest'],
    },
    description='A blog engine with flexible block contents (based on django-fluent-contents).',
    long_description=read('README.rst'),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-blogs',
    download_url='https://github.com/edoburu/django-fluent-blogs/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    test_suite = 'runtests',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
