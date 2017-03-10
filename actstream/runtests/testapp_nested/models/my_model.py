from django.db import models


class NestedModel(models.Model):
    text = models.TextField()

    class Meta:
        app_label = 'testapp_nested'

