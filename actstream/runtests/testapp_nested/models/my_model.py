import django
from django.db import models


class NestedModel(models.Model):
    text = models.TextField()

    class Meta:
        app_label = 'testapp_nested'


if django.VERSION[:2] < (1, 7):
    from actstream.runtests.testapp_nested.apps import TestappNestedConfig

    TestappNestedConfig().ready()
