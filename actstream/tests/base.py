import os
from json import loads
from datetime import datetime

from django.test import TestCase
from django.template.loader import Template, Context
from django.utils.six import text_type
from django.utils.timesince import timesince
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from actstream.registry import register, unregister
from actstream.compat import get_user_model
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
        for model in self.actstream_models:
            register(model)

    def assertSetEqual(self, l1, l2, msg=None):
        self.assertSequenceEqual(set(map(text_type, l1)), set(l2))

    def assertAllIn(self, bits, string):
        for bit in bits:
            self.assertIn(bit, string)

    def assertAllIn(self, bits, string):
        for bit in bits:
            self.assertIn(bit, string)

    def assertJSON(self, string):
        return loads(string)

    def tearDown(self):
        for model in self.actstream_models:
            unregister(model)

    def capture(self, url):
        name = url.strip('/').replace('/', '_')
        content = self.client.get(url).content.decode()
        if 'CAPTURE' in os.environ:
            with open(name, 'wb') as fh:
                fh.write(content)
        elif os.path.isfile(name):
            pass
        return content


class DataTestCase(ActivityBaseTestCase):
    actstream_models = ('auth.User', 'auth.Group', 'sites.Site')

    def setUp(self):
        self.testdate = datetime(2000, 1, 1)
        self.timesince = timesince(self.testdate).encode('utf8').replace(b'\xc2\xa0', b' ').decode()
        self.User = User = get_user_model()
        self.user_ct = ContentType.objects.get_for_model(User)
        super(DataTestCase, self).setUp()
        self.group = Group.objects.create(name='CoolGroup')
        self.user1 = User.objects.get_or_create(username='admin')[0]
        self.user1.set_password('admin')
        self.user1.is_superuser = self.user1.is_staff = True
        self.user1.save()
        self.user2 = User.objects.get_or_create(username='Two')[0]
        self.user3 = User.objects.get_or_create(username='Three')[0]

        # User1 joins group
        self.user1.groups.add(self.group)
        self.join_action = action.send(self.user1, verb='joined', target=self.group,
                                       timestamp=self.testdate)[0][1]

        # User1 follows User2
        follow(self.user1, self.user2, timestamp=self.testdate)

        # User2 joins group
        self.user2.groups.add(self.group)
        action.send(self.user2, verb='joined', target=self.group, timestamp=self.testdate)

        # User2 follows group
        follow(self.user2, self.group, timestamp=self.testdate)

        # User1 comments on group
        # Use a site object here and predict the "__unicode__ method output"
        action.send(self.user1, verb='commented on', target=self.group, timestamp=self.testdate)
        self.comment = Site.objects.create(
            domain="admin: Sweet Group!...")

        # Group responds to comment
        action.send(self.group, verb='responded to', target=self.comment, timestamp=self.testdate)

        # User 3 did something but doesn't following someone
        action.send(self.user3, verb='liked actstream', timestamp=self.testdate)
