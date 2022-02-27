from datetime import datetime
from unittest import skipUnless

from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from actstream.signals import action
from actstream.registry import register, unregister
from actstream.models import Action, actor_stream, model_stream
from actstream.tests.base import render, ActivityBaseTestCase, DataTestCase
from actstream.settings import USE_JSONFIELD, USE_DRF

from testapp.models import MyUser, Player, Abstract, Unregistered
from testapp_nested.models.my_model import NestedModel


class TestAppTests(ActivityBaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.User.objects.create(username='test')
        action.send(self.user, verb='was created')

    def test_accessor(self):
        self.assertEqual(len(Action.objects.testfoo(self.user)), 1)
        self.assertEqual(
            len(Action.objects.testfoo(self.user, datetime(1970, 1, 1))),
            0
        )

    def test_mystream(self):
        self.assertEqual(
            len(self.user.actor_actions.testbar('was created')),
            1
        )
        self.assertEqual(
            len(self.user.action_object_actions.testbar('was created')),
            0
        )

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

        self.assertEqual(
            self.capture(
                'testapp_custom_feed',
                'was created')['totalItems'],
            1
        )

    def test_customuser(self):
        from testapp.models import MyUser

        self.assertEqual(self.User, MyUser)
        self.assertEqual(self.user.get_full_name(), 'test')

    @skipUnless(USE_JSONFIELD, 'Django jsonfield disabled')
    def test_jsonfield(self):
        action.send(
            self.user, verb='said', text='foobar',
            tags=['sayings'],
            more_data={'pk': self.user.pk}
        )
        newaction = Action.objects.filter(verb='said')[0]
        self.assertEqual(newaction.data['text'], 'foobar')
        self.assertEqual(newaction.data['tags'], ['sayings'])
        self.assertEqual(newaction.data['more_data'], {'pk': self.user.pk})


@skipUnless(USE_DRF, 'Django rest framework disabled')
class DRFTestCase(DataTestCase):
    def setUp(self):
        from rest_framework.test import APIClient

        super().setUp()
        self.client = APIClient()
        self.client.login(username='admin', password='admin')

    def get(self, *args, **kwargs):
        return self.assertJSON(self.client.get(*args, **kwargs).content.decode())

    def test_actstream(self):
        actions = self.get('/api/actions/')
        self.assertEqual(len(actions), 11)
        follows = self.get('/api/follows/')
        self.assertEqual(len(follows), 6)

    def test_hyperlink(self):
        action = self.get('/api/actions/1/')
        self.assertEqual(action['timestamp'], '2000-01-01T00:00:00')
        self.assertStartsWith(action['actor'], 'http')

    def test_urls(self):
        from actstream.drf.urls import router

        registerd = [url[0] for url in router.registry]
        names = ['actions', 'follows', 'groups', 'sites',
                 'players', 'my users', 'nested models']
        self.assertSetEqual(registerd, names)
        endpoints = self.get('/api/')
        self.assertSetEqual(registerd, endpoints.keys())
        for url in registerd:
            objs = self.get(f'/api/{url}/')
            self.assertIsInstance(objs, list)
            if len(objs):
                obj = self.get(f'/api/{url}/{objs[0]["id"]}/')
                self.assertEqual(objs[0], obj)

    def test_serializers(self):
        from actstream.drf.serializers import registered_serializers as serializers
        from testapp.drf import GroupSerializer

        models = (Group, MyUser, Player, Site, NestedModel)
        self.assertSetEqual(serializers.keys(), models, domap=False)

        groups = self.get('/api/groups/')
        self.assertEqual(len(groups), 2)
        self.assertSetEqual(GroupSerializer.Meta.fields, groups[0].keys())
