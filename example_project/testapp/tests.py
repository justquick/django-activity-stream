from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from actstream.models import Action
from actstream.signals import action

class TestAppTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='test')
        action.send(self.user, verb='was created')

    def test_accessor(self):
        self.assertEqual(len(Action.objects.testfoo(self.user)), 1)
        self.assertEqual(len(Action.objects.testfoo(self.user, datetime(1970, 1, 1))), 0)

    def test_mystream(self):
        self.assertEqual(len(self.user.actor_actions.testbar('was created')), 1)
        self.assertEqual(len(self.user.action_object_actions.testbar('was created')), 0)
