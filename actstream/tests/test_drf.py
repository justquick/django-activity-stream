from unittest import skipUnless

from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from actstream.tests.base import DataTestCase
from actstream.settings import USE_DRF
from actstream.models import Action

from testapp.models import MyUser, Player
from testapp_nested.models.my_model import NestedModel


@skipUnless(USE_DRF, 'Django rest framework disabled')
class DRFTestCase(DataTestCase):
    def setUp(self):
        from rest_framework.test import APIClient

        super().setUp()
        self.client = APIClient()
        self.auth_client = APIClient()
        self.auth_client.login(username='admin', password='admin')

    def get(self, *args, **kwargs):
        auth = kwargs.pop('auth', False)
        client = self.auth_client if auth else self.client
        return client.get(*args, **kwargs).data

    def test_actstream(self):
        actions = self.get('/api/actions/')
        self.assertEqual(len(actions), 11)
        follows = self.get('/api/follows/')
        self.assertEqual(len(follows), 6)

    def test_hyperlink(self):
        action = self.get('/api/actions/1/')
        print('DEBUG',action)
        self.assertEqual(action['timestamp'], '2000-01-01T00:00:00')
        self.assertStartsWith(action['actor'], 'http')

    def test_urls(self):
        from actstream.drf.urls import router

        registerd = [url[0] for url in router.registry]
        names = ['actions', 'follows', 'groups', 'sites',
                 'players', 'my-users', 'nested-models']
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

    def test_viewset(self):
        resp = self.client.head('/api/groups/foo/')
        self.assertEqual(resp.status_code, 420)
        self.assertEqual(resp.data, ['chill'])

    def test_me(self):
        actions = self.get('/api/actions/me/', auth=True)
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0]['verb'], 'joined')

    def test_model(self):
        actions = self.get(f'/api/actions/model/{self.group_ct.id}/', auth=True)
        self.assertEqual(len(actions), 7)
        self.assertEqual(actions[0]['verb'], 'joined')

    def test_object(self):
        url = f'/api/actions/object/{self.group_ct.id}/{self.group.id}/'
        actions = self.get(url, auth=True)
        self.assertEqual(len(actions), 5)

    def test_action_send(self):
        body = {
            'verb': 'mentioned',
            'description': 'talked about a group',
            'target_content_type_id': self.group_ct.id,
            'target_object_id': self.group.id
        }
        post = self.auth_client.post('/api/actions/send/', body)
        self.assertEqual(post.status_code, 201)
        action = Action.objects.first()
        self.assertEqual(action.description, body['description'])
        self.assertEqual(action.verb, body['verb'])
        self.assertEqual(action.actor, self.user1)
        self.assertEqual(action.target, self.group)
