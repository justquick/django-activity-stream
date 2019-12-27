from django.db import models


class NotInstalledModel(models.Model):
    """A model that isn't in INSTALLED_APPS."""

    text = models.TextField()

    class Meta:
        app_label = 'notinstalled'
        managed = False
