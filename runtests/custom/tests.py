from django.test.utils import override_settings

from actstream import get_action_model, get_follow_model
from actstream.signals import action
from actstream.tests.base import ActivityBaseTestCase

from .models import CustomAction, CustomFollow


@override_settings(
    ACTSTREAM_ACTION_MODEL='custom.CustomAction',
    ACTSTREAM_FOLLOW_MODEL='custom.CustomFollow'
)
class CustomModelTests(ActivityBaseTestCase):
    def setUp(self):
        super(CustomModelTests, self).setUp()
        self.user = self.User.objects.create(username='test')

    def test_custom_action_model(self):
        self.assertEqual(get_action_model(), CustomAction)

    def test_custom_follow_model(self):
        self.assertEqual(get_follow_model(), CustomFollow)

    def test_custom_data(self):
        """Adding custom data to a model field works as expected."""
        action.send(self.user, verb='was created', quest='to be awesome')
        self.assertEqual(CustomAction.objects.count(), 1)
        self.assertEqual(CustomAction.objects.first().quest, 'to be awesome')
