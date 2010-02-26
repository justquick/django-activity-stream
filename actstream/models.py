from operator import or_
from django.db import models
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse
from django.utils.timesince import timesince as timesince_
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from actstream.signals import action

class FollowManager(models.Manager):
    def stream_for_user(self, user):
        """
        Produces a QuerySet of most recent activities from actors the user follows
        """
        qs = (Activity.objects.stream_for_actor(follow.actor) for follow in self.filter(user=user))
        return reduce(or_, qs).order_by('-timestamp')
    
class Follow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(User)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField() 
    actor = generic.GenericForeignKey()
    
    objects = FollowManager()
    
    def __unicode__(self):
        return u'%s -> %s' % (self.user, self.actor)

class ActivityManager(models.Manager):
    def stream_for_actor(self, actor):
        """
        Produces a QuerySet of most recent activities for any actor
        """
        return self.filter(
            actor_content_type = ContentType.objects.get_for_model(actor),
            actor_object_id = actor.pk,
        ).order_by('-timestamp')
        
    def stream_for_model(self, model):
        """
        Produces a QuerySet of most recent activities for any model
        """
        return self.filter(
            actor_content_type = ContentType.objects.get_for_model(model),
        ).order_by('-timestamp')
        
class Activity(models.Model):
    """
    Activity feed model
    nomenclature based on http://martin.atkins.me.uk/specs/activitystreams/atomactivity
    
    Generalized Format::
    
        <actor> <verb> <time>
        <actor> <verb> <target> <time>
    
    Examples::
    
        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        
    Unicode Representation::
    
        justquick reached level 60 1 minute ago
        
    HTML Representation::
    
        <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago

    """
    actor_content_type = models.ForeignKey(ContentType,related_name='actor')
    actor_object_id = models.PositiveIntegerField() 
    actor = generic.GenericForeignKey('actor_content_type','actor_object_id')
    
    verb = models.CharField(max_length=255)
    
    target_content_type = models.ForeignKey(ContentType,related_name='target',blank=True,null=True)
    target_object_id = models.PositiveIntegerField(blank=True,null=True) 
    target = generic.GenericForeignKey('target_content_type','target_object_id')
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = ActivityManager()
    
    def __unicode__(self):
        if self.target:
            return u'%s %s %s %s ago' % \
                (self.actor, self.verb, self.target, self.timesince())
        return u'%s %s %s ago' % (self.actor, self.verb, self.timesince())
        
    def actor_url(self):
        """
        Returns the actor stream of this activity's actor
        """
        return reverse('actstream_actor',None,(self.actor_content_type.pk,self.actor_object_id))
        
    def target_url(self):
        """
        Returns the actor stream of this activity's target
        """        
        return reverse('actstream_actor',None,(self.target_content_type.pk,self.target_object_id))
                
        
    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the activity's timestamp
        """
        return timesince_(self.timestamp, now)

    @models.permalink
    def get_absolute_url(self):
        return ('actstream.views.detail', [self.pk])
        

def follow(user, actor):
    """
    Links a ``User`` to any  ``Actor`` so that the actor's activities appear in the user's stream.
    Also sends the ``<user> started following <actor>`` signal.
    
    Syntax::
    
        follow(<user>, <actor>)
    
    Example::
    
        follow(request.user, group)
    
    """
    action.send(user, verb='started following', target=actor)
    return Follow.objects.get_or_create(
        user = user, object_id = actor.pk, 
        content_type = ContentType.objects.get_for_model(actor)
    )[0]
    
def actor_stream(actor):
    return Activity.objects.stream_for_actor(actor)
actor_stream.__doc__ = Activity.objects.stream_for_actor.__doc__
    
def user_stream(user):
    return Follow.objects.stream_for_user(user)
user_stream.__doc__ = Follow.objects.stream_for_user.__doc__
    
def model_stream(model):
    return Activity.objects.stream_for_model(model)
model_stream.__doc__ = Activity.objects.stream_for_model.__doc__

    
def action_handler(verb, target=None, **kwargs):
    actor = kwargs.pop('sender')
    activity = Activity.objects.get_or_create(
        actor_content_type = ContentType.objects.get_for_model(actor),
        actor_object_id = actor.pk,
        verb = verb
    )[0]
    if target:
        activity.target_object_id = target.pk
        activity.target_content_type = ContentType.objects.get_for_model(target)
        activity.save()
    
action.connect(action_handler)
