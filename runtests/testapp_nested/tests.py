from django.core.exceptions import ImproperlyConfigured

from actstream.registry import register, registry
from actstream.tests.base import ActivityBaseTestCase

from testapp_nested.models import my_model


class TestAppNestedTests(ActivityBaseTestCase):

    def test_registration(self):
        self.assertIn(my_model.NestedModel, registry)

    def test_not_installed(self):
        from notinstalled.models import NotInstalledModel
        self.assertRaises(ImproperlyConfigured, register, NotInstalledModel)
