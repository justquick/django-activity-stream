from django.utils.six.moves.urllib.parse import urlencode

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from actstream import models
from actstream.tests.base import DataTestCase


class ViewsTest(DataTestCase):
    def setUp(self):
        super(ViewsTest, self).setUp()
        self.client.login(username='admin', password='admin')

    def get(self, viewname, *args, **params):
        return self.client.get('%s?%s' % (reverse(viewname, args=args),
                                          urlencode(params)))

    def assertQSEqual(self, qs1, qs2):
        attrs = lambda item: dict([(key, value)
                                   for key, value in item.__dict__.items()
                                   if not key.startswith('_')])
        self.assertEqual(len(qs1), len(qs2))
        for i, item in enumerate(qs1):
            self.assertDictEqual(attrs(item), attrs(qs2[i]))

    def test_follow_unfollow(self):
        response = self.get('actstream_follow', self.user_ct.pk, self.user3.pk)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.templates), 0)
        follow = {'user': self.user1, 'content_type': self.user_ct,
                  'object_id': self.user3.pk}
        action = {'actor_content_type': self.user_ct, 'actor_object_id': self.user1.pk,
                  'target_content_type': self.user_ct, 'target_object_id': self.user3.pk,
                  'verb': 'started following'}
        models.Follow.objects.get(**follow)
        models.Action.objects.get(**action)

        response = self.get('actstream_unfollow', self.user_ct.pk, self.user3.pk)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(response.templates), 0)
        self.assertRaises(models.Follow.DoesNotExist, models.Follow.objects.get, **follow)

        response = self.get('actstream_unfollow', self.user_ct.pk, self.user3.pk, next='/redirect/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/redirect/'))

    def test_stream(self):
        response = self.get('actstream')
        self.assertTemplateUsed(response, 'actstream/actor.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertEqual(response.context['actor'], self.user1)
        self.assertEqual(response.context['ctype'], self.user_ct)
        self.assertQSEqual(response.context['action_list'],
                           models.user_stream(self.user1))

    def test_followers_following(self):
        response = self.get('actstream_followers', self.user_ct.pk, self.user2.pk)
        self.assertTemplateUsed(response, 'actstream/followers.html')
        self.assertEqual(response.context['user'], self.user1)
        self.assertQSEqual(response.context['followers'],
                           models.followers(self.user2))

        response = self.get('actstream_following', self.user2.pk)
        self.assertTemplateUsed(response, 'actstream/following.html')
        self.assertEqual(response.context['user'], self.user2)
        self.assertQSEqual(response.context['following'],
                           models.following(self.user2))

    def test_user(self):
        response = self.get('actstream_user', self.user2.username)
        self.assertTemplateUsed(response, 'actstream/actor.html')
        self.assertEqual(response.context['ctype'], self.user_ct)
        self.assertEqual(response.context['actor'], self.user2)
        self.assertQSEqual(response.context['action_list'],
                           models.user_stream(self.user2))

    def test_detail(self):
        response = self.get('actstream_detail', self.join_action.pk)
        self.assertTemplateUsed(response, 'actstream/detail.html')
        self.assertTemplateUsed(response, 'actstream/action.html')
        self.assertEqual(response.context['action'], self.join_action)

    def test_actor(self):
        response = self.get('actstream_actor', self.user_ct.pk, self.user2.pk)
        self.assertTemplateUsed(response, 'actstream/actor.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertEqual(response.context['ctype'], self.user_ct)
        self.assertEqual(response.context['actor'], self.user2)
        self.assertQSEqual(response.context['action_list'],
                           models.actor_stream(self.user2))

    def test_model(self):
        response = self.get('actstream_model', self.user_ct.pk)
        self.assertTemplateUsed(response, 'actstream/actor.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertEqual(response.context['ctype'], self.user_ct)
        self.assertEqual(response.context['actor'], self.user_ct.model_class())
        self.assertQSEqual(response.context['action_list'],
                           models.model_stream(self.user1))
