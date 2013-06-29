from datetime import datetime

import django
from django.utils.unittest import skipUnless
from django.test import TestCase

from actstream.models import Action
from actstream.signals import action
from actstream.compat import get_user_model


User = get_user_model()


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

    def test_jsonfield(self):
        action.send(self.user, verb='said', text='foobar', tags=['sayings'],
                    more_data={'pk': self.user.pk})
        newaction = Action.objects.filter(verb='said')[0]
        self.assertEqual(newaction.data['text'], 'foobar')
        self.assertEqual(newaction.data['tags'], ['sayings'])
        self.assertEqual(newaction.data['more_data'], {'pk': self.user.pk})

    @skipUnless(django.VERSION[0] == 1 and django.VERSION[1] >= 5, 'Django>=1.5 Required')
    def test_customuser(self):
        from testapp.models import MyUser

        self.assertEqual(User, MyUser)
        self.assertEqual(self.user.get_full_name(), 'full')
