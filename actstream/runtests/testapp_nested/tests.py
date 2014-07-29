from actstream import registry
from actstream.tests import ActivityBaseTestCase

from testapp_nested.models import my_model


class TestAppNestedTests(ActivityBaseTestCase):
    def test_registration(self):
        registry.register(my_model.NestedModel)
