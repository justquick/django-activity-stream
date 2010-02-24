import unittest
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from actstream import action, follow
from actstream.models import Activity, Follow
from actstream.util import *

class Player(models.Model):
    state = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '#%d' % self.pk

class ActivityTestCase(unittest.TestCase):
    def setUp(self):
        self.group = Group.objects.get_or_create(name='CoolGroup')[0]
        self.user1 = User.objects.get_or_create(username='One')[0]
        self.user2 = User.objects.get_or_create(username='Two')[0]
        
        # User1 joins group
        self.user1.groups.add(self.group)
        action.send(self.user1,verb='joined',target=self.group)
        
        # User1 follows User2
        follow(self.user1, self.user2)
        
        # User2 joins group        
        self.user2.groups.add(self.group)
        action.send(self.user2,verb='joined',target=self.group)
        
        # User2 follows group
        follow(self.user2, self.group)
        
        # User1 comments on group
        action.send(self.user1,verb='commented on',target=self.group)
        comment = Comment.objects.get_or_create(
            user = self.user1,
            content_type = ContentType.objects.get_for_model(self.group),
            object_pk = self.group.pk,
            comment = 'Sweet Group!',
            site = Site.objects.get_current()
        )[0]
        
        # Group responds to comment
        action.send(self.group,verb='responded to',target=comment)

    def test_user1(self):
        self.assertEqual(map(unicode, actor_stream(self.user1)),
            [u'One commented on CoolGroup 0 minutes ago', u'One started following Two 0 minutes ago', u'One joined CoolGroup 0 minutes ago'])
        
    def test_user2(self):
        self.assertEqual(map(unicode, actor_stream(self.user2)),
            [u'Two started following CoolGroup 0 minutes ago', u'Two joined CoolGroup 0 minutes ago'])
        
    def test_group(self):
        self.assertEqual(map(unicode, actor_stream(self.group)),
            [u'CoolGroup responded to One: Sweet Group!... 0 minutes ago'])
        
    def test_stream(self):
        self.assertEqual(map(unicode, user_stream(self.user1)),
            [u'Two started following CoolGroup 0 minutes ago', u'Two joined CoolGroup 0 minutes ago'])
        self.assertEqual(map(unicode, user_stream(self.user2)),
            [u'CoolGroup responded to One: Sweet Group!... 0 minutes ago'])
        
    def test_zombies(self):
        from random import choice, randint
        from time import sleep
        
        humans = [Player.objects.create() for i in range(100)]
        zombies = [Player.objects.create(state=1) for _ in range(2)]

        while len(humans):
            for z in zombies:
                if not len(humans): break
                victim = choice(humans)
                humans.pop(humans.index(victim))
                victim.state = 1
                victim.save()
                zombies.append(victim)
                action.send(z,verb='killed',target=victim)
                
        self.assertEqual(map(unicode,model_stream(Player))[:5],
            map(unicode,Activity.objects.order_by('-timestamp')[:5]))