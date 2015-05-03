from datetime import datetime

import django
from django.core.exceptions import ImproperlyConfigured

from actstream.signals import action
from actstream.registry import register, unregister
from actstream.models import Action, actor_stream, model_stream
from actstream.tests.base import render, ActivityBaseTestCase
from actstream.settings import USE_JSONFIELD

from actstream.runtests.testapp.models import Abstract, Unregistered


class TestAppTests(ActivityBaseTestCase):
    def setUp(self):
        super(TestAppTests, self).setUp()
        self.user = self.User.objects.create(username='test')
        action.send(self.user, verb='was created')

    def test_accessor(self):
        self.assertEqual(len(Action.objects.testfoo(self.user)), 1)
        self.assertEqual(len(Action.objects.testfoo(self.user, datetime(1970, 1, 1))), 0)

    def test_mystream(self):
        self.assertEqual(len(self.user.actor_actions.testbar('was created')), 1)
        self.assertEqual(len(self.user.action_object_actions.testbar('was created')), 0)

    def test_registration(self):
        instance = Unregistered.objects.create(name='fubar')
        self.assertRaises(ImproperlyConfigured, actor_stream, instance)
        register(Unregistered)
        self.assertEqual(actor_stream(instance).count(), 0)

        self.assertRaises(RuntimeError, model_stream, Abstract)
        self.assertRaises(ImproperlyConfigured, register, Abstract)
        unregister(Unregistered)

    def test_tag_custom_activity_stream(self):
        stream = self.user.actor_actions.testbar('was created')
        output = render('''{% activity_stream 'testbar' 'was created' %}
        {% for action in stream %}
            {{ action }}
        {% endfor %}
        ''', user=self.user)
        self.assertAllIn([str(action) for action in stream], output)

        self.assertEqual(self.capture('testapp_custom_feed',
                                      'was created')['totalItems'], 1)

    def test_customuser(self):
        if django.VERSION[:2] >= (1, 5):
            from actstream.runtests.testapp.models import MyUser

            self.assertEqual(self.User, MyUser)
            self.assertEqual(self.user.get_full_name(), 'test')

    if USE_JSONFIELD:
        def test_jsonfield(self):
            action.send(self.user, verb='said', text='foobar', tags=['sayings'],
                        more_data={'pk': self.user.pk})
            newaction = Action.objects.filter(verb='said')[0]
            self.assertEqual(newaction.data['text'], 'foobar')
            self.assertEqual(newaction.data['tags'], ['sayings'])
            self.assertEqual(newaction.data['more_data'], {'pk': self.user.pk})
