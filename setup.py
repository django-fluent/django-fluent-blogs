#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import dirname, join
import sys, os

# When creating the sdist, make sure the django.mo file also exists:
try:
    os.chdir('fluent_blogs')
    from django.core.management.commands.compilemessages import compile_messages
    compile_messages(sys.stderr)
finally:
    os.chdir('..')


setup(
    name='django-fluent-blogs',
    version='0.1.0',
    license='Apache License, Version 2.0',

    install_requires=[
        'Django>=1.3.0',
        'django-categories>=1.0.0',
    ],
    extras_require = {
        'taggit': ['taggit', 'taggit-autocomplete-modified'],
        'blogpage': ['django-fluent-pages'],
    },
    description='A blog engine based on django-fluent-contents.',
    long_description=open('README.rst').read(),

    author='Diederik van der Boor',
    author_email='opensource@edoburu.nl',

    url='https://github.com/edoburu/django-fluent-blogs',
    download_url='https://github.com/edoburu/django-fluent-blogs/zipball/master',

    packages=find_packages(),
    include_package_data=True,

    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
