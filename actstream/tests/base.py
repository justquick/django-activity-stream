from json import loads
from datetime import datetime
from inspect import getargspec

from django.apps import apps
from django.test import TestCase
from django.template import Template, Context
from django.utils.timesince import timesince
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from actstream.models import Action, Follow
from actstream.registry import register, unregister
from actstream.actions import follow
from actstream.signals import action


def render(src, **ctx):
    return Template('{% load activity_tags %}' + src).render(Context(ctx))


class LTE(int):
    def __new__(cls, n):
        obj = super(LTE, cls).__new__(cls, n)
        obj.n = n
        return obj

    def __eq__(self, other):
        return other <= self.n

    def __repr__(self):
        return "<= %s" % self.n


class ActivityBaseTestCase(TestCase):
    actstream_models = ()
    maxDiff = None

    def setUp(self):
        self.User = get_user_model()
        self.user_ct = ContentType.objects.get_for_model(self.User)
        register(self.User)
        for model in self.actstream_models:
            register(model)

    def assertSetEqual(self, l1, l2, msg=None, domap=True):
        if domap:
            l1 = map(str, l1)
        self.assertSequenceEqual(set(l1), set(l2), msg)

    def assertAllIn(self, bits, obj):
        for bit in bits:
            self.assertIn(bit, str(obj))

    def assertJSON(self, string):
        return loads(string)

    def tearDown(self):
        for model in self.actstream_models:
            model = apps.get_model(*model.split('.'))
            unregister(model)
            model.objects.all().delete()
        Action.objects.all().delete()
        Follow.objects.all().delete()
        self.User.objects.all().delete()

    def capture(self, viewname, *args, query_string=''):
        response = self.client.get('{}?{}'.format(reverse(viewname, args=args),query_string))
        content = response.content.decode()
        if response['Content-Type'] == 'application/json':
            return loads(content)
        return content


class DataTestCase(ActivityBaseTestCase):
    actstream_models = ('auth.Group', 'sites.Site')

    def setUp(self):
        self.testdate = datetime(2000, 1, 1)
        self.timesince = timesince(self.testdate).encode('utf8').replace(
            b'\xc2\xa0', b' ').decode()
        self.group_ct = ContentType.objects.get_for_model(Group)
        super(DataTestCase, self).setUp()
        self.group = Group.objects.create(name='CoolGroup')
        self.another_group = Group.objects.create(name='NiceGroup')
        if 'email' in getargspec(self.User.objects.create_superuser).args:
            self.user1 = self.User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.user2 = self.User.objects.create_user('Two', 'two@example.com')
            self.user3 = self.User.objects.create_user('Three', 'three@example.com')
            self.user4 = self.User.objects.create_user('Four', 'four@example.com')
        else:
            self.user1 = self.User.objects.create_superuser('admin', 'admin')
            self.user2 = self.User.objects.create_user('Two')
            self.user3 = self.User.objects.create_user('Three')
            self.user4 = self.User.objects.create_user('Four')
        # User1 joins group
        self.user1.groups.add(self.group)
        self.join_action = action.send(self.user1, verb='joined',
                                       target=self.group,
                                       timestamp=self.testdate)[0][1]

        # User1 follows User2
        follow(self.user1, self.user2, timestamp=self.testdate)

        # User2 joins group
        self.user2.groups.add(self.group)
        action.send(self.user2, verb='joined', target=self.group,
                    timestamp=self.testdate)

        # User2 follows group
        follow(self.user2, self.group, timestamp=self.testdate)

        # User1 comments on group
        # Use a site object here and predict the "__unicode__ method output"
        action.send(self.user1, verb='commented on', target=self.group,
                    timestamp=self.testdate)

        self.comment = Site.objects.create(
            domain="admin: Sweet Group!...")

        # Group responds to comment
        action.send(self.group, verb='responded to', target=self.comment,
                    timestamp=self.testdate)

        # User 3 did something but doesn't following someone
        action.send(self.user3, verb='liked actstream', timestamp=self.testdate)

        # User4 likes group
        follow(self.user4, self.another_group, timestamp=self.testdate, flag='liking')
        # User4 watches group
        follow(self.user4, self.another_group, timestamp=self.testdate, flag='watching')
        # User4 likes User1
        follow(self.user4, self.user1, timestamp=self.testdate, flag='liking')
        # User4 blacklist user3
        follow(self.user4, self.user3, timestamp=self.testdate, flag='blacklisting')
