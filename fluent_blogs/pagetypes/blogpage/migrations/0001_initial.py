# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPage',
            fields=[
                ('urlnode_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_pages.UrlNode')),
            ],
            options={
                'db_table': 'pagetype_blogpage_blogpage',
                'verbose_name': 'Blog module',
                'verbose_name_plural': 'Blog modules',
            },
            bases=('fluent_pages.htmlpage',),
        ),
    ]
