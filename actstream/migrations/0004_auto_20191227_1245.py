# Generated by Django 2.1.11 on 2019-12-27 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actstream', '0003_add_follow_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='action_object_object_id',
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='action',
            name='actor_object_id',
            field=models.UUIDField(db_index=True),
        ),
        migrations.AlterField(
            model_name='action',
            name='target_object_id',
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='follow',
            name='object_id',
            field=models.UUIDField(db_index=True),
        ),
    ]