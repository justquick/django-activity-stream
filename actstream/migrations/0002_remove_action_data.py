# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from actstream.settings import USE_JSONFIELD


class Migration(migrations.Migration):
    dependencies = [
        ('actstream', '0001_initial'),
    ]

    if not USE_JSONFIELD:
        operations = [
            migrations.RemoveField(
                model_name='action',
                name='data',
            ),
        ]
