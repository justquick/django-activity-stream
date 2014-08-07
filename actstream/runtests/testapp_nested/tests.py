from django.db import models
from django.core.exceptions import ImproperlyConfigured

from actstream.registry import register, registry
from actstream.tests import ActivityBaseTestCase

from testapp_nested.models import my_model


class NotInstalledModel(models.Model):
    text = models.TextField()

    class Meta:
        app_label = 'testapp_not_installed'


class TestAppNestedTests(ActivityBaseTestCase):
    def test_registration(self):
        register(my_model.NestedModel)
        self.assertIn(my_model.NestedModel, registry)

    def test_not_installed(self):
        self.assertRaises(ImproperlyConfigured, register, NotInstalledModel)
