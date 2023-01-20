from django.test.utils import override_settings

from actstream.settings import get_action_model, get_follow_model
from actstream.signals import action
from actstream.tests.base import ActivityBaseTestCase
from actstream.actions import follow, unfollow

from .models import CustomAction, CustomFollow


@override_settings(
    ACTSTREAM_ACTION_MODEL='custom.CustomAction',
    ACTSTREAM_FOLLOW_MODEL='custom.CustomFollow'
)
class CustomModelTests(ActivityBaseTestCase):
    def setUp(self):
        super(CustomModelTests, self).setUp()
        self.user1 = self.User.objects.create(username='test1')
        self.user2 = self.User.objects.create(username='test2')

    def test_custom_action_model(self):
        self.assertEqual(get_action_model(), CustomAction)

    def test_custom_follow_model(self):
        self.assertEqual(get_follow_model(), CustomFollow)

    def test_custom_data(self):
        """Adding custom data to a model field works as expected."""
        action.send(self.user1, verb='was created', quest='to be awesome')
        self.assertEqual(CustomAction.objects.count(), 1)
        self.assertEqual(CustomAction .objects.first().quest, 'to be awesome')

    def test_custom_follow(self):
        follow(self.user1, self.user2, is_special=True, quest='holy grail')
        custom_follow = get_follow_model().objects.first()
        self.assertEqual(custom_follow.user, self.user1)
        self.assertEqual(custom_follow.follow_object, self.user2)
        self.assertEqual(custom_follow.is_special, True)
        custom_action = get_action_model().objects.first()
        self.assertEqual(custom_action.actor, self.user1)
        self.assertEqual(custom_action.target, self.user2)
        self.assertEqual(custom_action.quest, 'holy grail')

        unfollow(self.user1, self.user2)
        self.assertFalse(get_follow_model().objects.exists())
