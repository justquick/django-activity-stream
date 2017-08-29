# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings

from actstream.settings import USE_JSONFIELD

if USE_JSONFIELD:
    from jsonfield_compat.fields import JSONField as DataField
else:
    DataField = models.TextField


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, help_text='', auto_created=True)),
                ('actor_object_id', models.CharField(max_length=255, db_index=True, help_text='')),
                ('verb', models.CharField(max_length=255, db_index=True, help_text='')),
                ('description', models.TextField(blank=True, null=True, help_text='')),
                ('target_object_id', models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text='')),
                ('action_object_object_id', models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text='')),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now, help_text='')),
                ('public', models.BooleanField(db_index=True, default=True, help_text='')),
                ('data', DataField(blank=True, null=True, help_text='')),
                ('action_object_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, blank=True, null=True, help_text='', related_name='action_object', to='contenttypes.ContentType')),
                ('actor_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, help_text='', related_name='actor', to='contenttypes.ContentType')),
                ('target_content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, blank=True, null=True, help_text='', related_name='target', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, help_text='', auto_created=True)),
                ('object_id', models.CharField(max_length=255, db_index=True, help_text='')),
                ('actor_only', models.BooleanField(verbose_name='Only follow actions where the object is the target.', default=True, help_text='')),
                ('started', models.DateTimeField(db_index=True, default=django.utils.timezone.now, help_text='')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, help_text='', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, help_text='', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set([('user', 'content_type', 'object_id')]),
        ),
    ]
