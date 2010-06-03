import unittest
from django.db import models
from django.test.client import Client
from django.contrib.auth.models import User, Group
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from actstream.signals import action
from actstream.models import Action, Follow, follow, user_stream, model_stream, actor_stream
from testapp.models import Player

class ActivityTestCase(unittest.TestCase):
    def setUp(self):
        self.group = Group.objects.get_or_create(name='CoolGroup')[0]
        self.user1 = User.objects.get_or_create(username='admin')[0]
        self.user1.set_password('admin')
        self.user1.is_superuser = self.user1.is_active = self.user1.is_staff = True
        self.user1.save()
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
        
        self.client = Client()

    def test_user1(self):
        self.assertEqual(map(unicode, actor_stream(self.user1)),
            [u'admin commented on CoolGroup 0 minutes ago', u'admin started following Two 0 minutes ago', u'admin joined CoolGroup 0 minutes ago'])
        
    def test_user2(self):
        self.assertEqual(map(unicode, actor_stream(self.user2)),
            [u'Two started following CoolGroup 0 minutes ago', u'Two joined CoolGroup 0 minutes ago'])
        
    def test_group(self):
        self.assertEqual(map(unicode, actor_stream(self.group)),
            [u'CoolGroup responded to admin: Sweet Group!... 0 minutes ago'])
        
    def test_stream(self):
        self.assertEqual(map(unicode, user_stream(self.user1)),
            [u'Two started following CoolGroup 0 minutes ago', u'Two joined CoolGroup 0 minutes ago'])
        self.assertEqual(map(unicode, user_stream(self.user2)),
            [u'CoolGroup responded to admin: Sweet Group!... 0 minutes ago'])
        
    def test_rss(self):
        rss = self.client.get('/feed/').content
        self.assert_(rss.startswith('<?xml version="1.0" encoding="utf-8"?>\n<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">'))
        self.assert_(rss.find('Activity feed for your followed actors')>-1)
    
    def test_atom(self):
        atom = self.client.get('/feed/atom/').content
        self.assert_(atom.startswith('<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en-us">'))
        self.assert_(atom.find('Activity feed for your followed actors')>-1)
        
    def test_zombies(self):
        from random import choice, randint
        
        humans = [Player.objects.create() for i in range(10)]
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
            map(unicode,Action.objects.order_by('-timestamp')[:5]))
        
    def tearDown(self):
        from django.core.serializers import serialize
        for i,m in enumerate((Comment,ContentType,Player,Follow,Action,User,Group)):
            f = open('testdata%d.json'%i,'w')
            f.write(serialize('json',m.objects.all()))
            f.close()
        Action.objects.all().delete()
        Comment.objects.all().delete()
        Player.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        Follow.objects.all().delete()
