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