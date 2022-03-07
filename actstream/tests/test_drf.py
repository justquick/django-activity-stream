from unittest import skipUnless
from json import loads


from django.urls import reverse

from actstream.tests.base import DataTestCase
from actstream.settings import USE_DRF, DRF_SETTINGS
from actstream.models import Action, Follow
from actstream import signals


class BaseDRFTestCase(DataTestCase):
    def setUp(self):
        from rest_framework.test import APIClient

        super().setUp()
        self.auth_user = self.user1
        self.client = APIClient()
        self.auth_client = APIClient()
        self.auth_client.login(username=self.user1.username, password='admin')

    def get(self, *args, **kwargs):
        auth = kwargs.pop('auth', False)
        client = self.auth_client if auth else self.client
        return client.get(*args, **kwargs).data

    def _check_urls(self, *urls):
        from actstream.drf.urls import router

        registerd = [url[0] for url in router.registry]
        root = reverse('api-root')
        for url in urls:
            assert url in registerd
            objs = self.get(f'{root}{url}/', auth=True)
            assert isinstance(objs, list)
            if len(objs):
                obj = self.get(f'{root}{url}/{objs[0]["id"]}/', auth=True)
                assert objs[0] == obj


@skipUnless(USE_DRF, 'Django rest framework disabled')
class DRFActionTestCase(BaseDRFTestCase):

    def test_actstream(self):
        actions = self.get(reverse('action-list'))
        assert len(actions) == 11
        follows = self.get(reverse('follow-list'))
        assert len(follows) == 6

    @skipUnless(DRF_SETTINGS['HYPERLINK_FIELDS'], 'Related hyperlinks disabled')
    def test_hyperlink_fields(self):
        actions = self.get(reverse('action-list'))
        action = self.get(reverse('action-detail', args=[actions[0]["id"]]))
        assert action['timestamp'].startswith('2000-01-01T00:00:00')
        assert action['actor'].startswith('http')

    @skipUnless(DRF_SETTINGS['EXPAND_FIELDS'], 'Related expanded fields disabled')
    def test_expand_fields(self):
        actions = self.get(reverse('action-list'))
        action = self.get(reverse('action-detail', args=[actions[0]["id"]]))
        assert action['timestamp'].startswith('2000-01-01T00:00:00')
        self.assertIsInstance(action['target'], dict)
        assert action['target']['username'] == 'Three'

    def test_urls(self):
        self._check_urls('actions', 'follows')

    def test_permissions(self):
        users = self.get(reverse('myuser-list'))
        assert str(users['detail']) == 'Authentication credentials were not provided.'
        users = self.get(reverse('myuser-list'), auth=True)
        assert len(users) == 4

    def test_model_fields(self):
        sites = self.get(reverse('site-list'))
        self.assertSetEqual(sites[0].keys(), ['id', 'domain'])

    def test_viewset(self):
        resp = self.client.head(reverse('group-foo'))
        assert resp.status_code == 420
        assert resp.data == ['chill']

    def test_my_actions(self):
        actions = self.get(reverse('action-my-actions'), auth=True)
        assert len(actions) == 3
        assert actions[0]['verb'] == 'joined'

    def test_model(self):
        actions = self.get(reverse('action-model-stream', args=[self.group_ct.id]), auth=True)
        assert len(actions) == 7
        assert actions[0]['verb'] == 'joined'

    def test_target(self):
        actions = self.get(reverse('action-target-stream', args=[self.group_ct.id, self.another_group.id]), auth=True)
        assert len(actions) == 2
        assert actions[0]['target']['name'] == actions[1]['target']['name'] == 'NiceGroup'

    def test_action_object(self):
        signals.action.send(self.user1, verb='created comment',
                            action_object=self.comment, target=self.group,
                            timestamp=self.testdate)[0][1]
        url = reverse('action-action-object-stream', args=[self.site_ct.id, self.comment.id])
        actions = self.get(url, auth=True)
        assert len(actions) == 1
        assert actions[0]['verb'] == 'created comment'

    def test_any(self):
        url = reverse('action-any-stream', args=[self.user_ct.id, self.auth_user.id])
        actions = self.get(url, auth=True)
        assert len(actions) == 4
        assert actions[0]['verb'] == 'joined'

    def test_following(self):
        actions = self.get(reverse('action-following'), auth=True)
        assert len(actions) == 2
        assert actions[0]['actor']['username'] == actions[1]['actor']['username'] == 'Two'

    def test_action_send(self):
        body = {
            'verb': 'mentioned',
            'description': 'talked about a group',
            'target_content_type_id': self.group_ct.id,
            'target_object_id': self.group.id
        }
        post = self.auth_client.post(reverse('action-send'), body)
        assert post.status_code == 201
        action = Action.objects.first()
        assert action.description == body['description']
        assert action.verb == body['verb']
        assert action.actor == self.user1
        assert action.target == self.group


@skipUnless(USE_DRF, 'Django rest framework disabled')
class DRFFollowTestCase(BaseDRFTestCase):
    def test_follow(self):
        body = {
            'content_type_id': self.site_ct.id,
            'object_id': self.comment.id
        }
        post = self.auth_client.post(reverse('follow-follow'), body)
        assert post.status_code == 201
        follow = Follow.objects.order_by('-id').first()
        assert follow.follow_object == self.comment
        assert follow.user == self.user1
        assert follow.user == self.user1
        assert follow.user == self.user1

    def test_is_following(self):
        url = reverse('follow-is-following', args=[self.site_ct.id, self.comment.id])
        resp = self.auth_client.get(url)
        data = loads(resp.data)
        assert not data['is_following']

        url = reverse('follow-is-following', args=[self.user_ct.id, self.user2.id])
        resp = self.auth_client.get(url)
        data = loads(resp.data)
        assert data['is_following']

    def test_followers(self):
        followers = self.auth_client.get(reverse('follow-followers')).data
        assert len(followers) == 1
        assert followers[0]['username'] == 'Four'

    def test_following(self):
        following = self.auth_client.get(reverse('follow-following')).data
        assert len(following) == 1
        assert following[0]['follow_object']['username'] == 'Two'
