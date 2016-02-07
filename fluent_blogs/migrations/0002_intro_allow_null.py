# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_blogs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry_translation',
            name='intro',
            field=models.TextField(null=True, verbose_name='Introtext'),
        ),
    ]
