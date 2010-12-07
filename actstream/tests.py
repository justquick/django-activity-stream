import unittest

from django.db import models
from django.test.client import Client
from django.test import TransactionTestCase
from django.template import Template, Context, RequestContext
from django.http import HttpRequest
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

from actstream.signals import action
from actstream.models import Action, Follow, follow, user_stream, model_stream, actor_stream

class ActivityTestCase(TransactionTestCase):
    urls = 'actstream.urls'    
    
    def setUp(self):
        self._urlconf_setup()
        
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
        self.comment = Comment.objects.create(
            user = self.user1,
            comment="Sweet Group!")
        
        # Group responds to comment
        action.send(self.group,verb='responded to',target=self.comment)
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
        
        humans = [User.objects.create(username='human%d' % i) for i in range(10)]
        zombies = [User.objects.create(username='zombie%d' % j) for j in range(2)]
    
        while len(humans):
            for z in zombies:
                if not len(humans): break
                victim = choice(humans)
                humans.pop(humans.index(victim))
                victim.save()
                zombies.append(victim)
                action.send(z,verb='killed',target=victim)
                
        self.assertEqual(map(unicode,model_stream(User))[:5],
            map(unicode,Action.objects.order_by('-timestamp')[:5]))
        
    def test_action_object(self):
        action.send(self.user1,verb='created comment',action_object=self.comment,target=self.group)
        created_action = Action.objects.get(verb='created comment')

        self.assertEqual(created_action.actor, self.user1)
        self.assertEqual(created_action.action_object, self.comment)
        self.assertEqual(created_action.target, self.group)
        self.assertEqual(unicode(created_action), u'admin created comment admin: Sweet Group!... on CoolGroup 0 minutes ago')

    def test_doesnt_generate_duplicate_follow_records(self):
        g = Group.objects.get_or_create(name='DupGroup')[0]
        s = User.objects.get_or_create(username='dupuser')[0]
        
        f1 = follow(s, g)
        self.assertTrue(f1 is not None, "Should have received a new follow record")
        self.assertTrue(isinstance(f1, Follow), "Returns a Follow object")
        
        self.assertEquals( 1, Follow.objects.filter(user = s, object_id = g.pk, 
            content_type = ContentType.objects.get_for_model(g)).count(), "Should only have 1 follow record here")
        
        f2 = follow(s, g)
        self.assertEquals( 1, Follow.objects.filter(user = s, object_id = g.pk, 
            content_type = ContentType.objects.get_for_model(g)).count(), "Should still only have 1 follow record here")
        self.assertTrue( f2 is not None, "Should have received a Follow object")
        self.assertTrue(isinstance(f2, Follow), "Returns a Follow object")
        self.assertEquals(f1, f2, "Should have received the same Follow object that I first submitted")

    def test_tag_display_action_rendered(self):
        an_action = Action.objects.all()[0]
        t = Template('{% load activity_tags %}{% display_action the_action %}')
        r = HttpRequest()
        c = RequestContext(r, { 'the_action' : an_action })
        result = t.render(c)
        self.assertTrue(result.find(str(an_action.actor)) > -1)
        self.assertTrue(result.find('/actors/') > -1)
        self.assertTrue(result.find(str(an_action.target)) > -1)

    def test_tag_display_action_rendered_into_variable(self):
        an_action = Action.objects.all()[0]
        t = Template('{% load activity_tags %}{% display_action the_action as thevar %}')
        r = HttpRequest()
        c = RequestContext(r, { 'the_action' : an_action })
        result = t.render(c)
        self.assertEquals("", result, "Returns an empty string when passing in 'as <varname>'")
        self.assertTrue(c['thevar'].find(str(an_action.actor)) > -1)
        self.assertTrue(c['thevar'].find('/actors/') > -1)
        self.assertTrue(c['thevar'].find(str(an_action.target)) > -1)

    def test_tag_get_user_contenttype(self):
        c = Context()
        user_content_type = ContentType.objects.get_for_model(User)

        t = Template('{% load activity_tags %}{% get_user_contenttype %}')
        t.render(c)
        '''
        i don't think this was intentional, but this unit test will cover this to ensure
        any change in the future to the tag still work for anyone using it.
        '''
        self.assertEquals(user_content_type, c['get_user_contenttype'], 
            "User ContentType object has been inserted into the context as the tag name")

        t = Template('{% load activity_tags %}{% get_user_contenttype as user_ctype %}{{ user_ctype.id }}')
        results = t.render(c)
        expected_user_content_type_id = '%d' % user_content_type.id
        self.assertEquals(expected_user_content_type_id, results, 
            "Tags load, execute and return the correct result")
        self.assertEquals(user_content_type, c['user_ctype'], 
            "User ContentType object has been inserted into the context as the specified variable")

    def tearDown(self):
        Action.objects.all().delete()
        User.objects.all().delete()
        Comment.objects.all().delete()
        Group.objects.all().delete()
        Follow.objects.all().delete()

class Comment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User)
    
    def __unicode__(self):
        return "%s: %s..." % (self.user.username , self.comment)

