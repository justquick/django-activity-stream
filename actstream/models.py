from datetime import datetime
from operator import or_
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings

from actstream.signals import action
from actstream.managers import FollowManager, ActionManager
from actstream.utils import get_class

action_manager_path = getattr(settings, 'ACTSTREAM_ACTION_MANAGER', None)
if action_manager_path:
    action_manager_class = get_class(action_manager_path)
else:
    action_manager_class = ActionManager
    
follow_manager_path = getattr(settings, 'ACTSTREAM_FOLLOW_MANAGER', None)
if follow_manager_path:
    follow_manager_class = get_class(follow_manager_path)
else:
    follow_manager_class = FollowManager

class Action(models.Model):
    """
    Action model describing the actor acting out a verb (on an optional target).
    Nomenclature based on http://martin.atkins.me.uk/specs/activitystreams/atomactivity

    Generalized Format::

        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::

        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <about 3 hours ago>

    Unicode Representation::

        justquick reached level 60 1 minute ago
        mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

    HTML Representation::

        <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago

    """
    actor_content_type = models.ForeignKey(ContentType,related_name='actor')
    actor_object_id = models.PositiveIntegerField()
    actor = generic.GenericForeignKey('actor_content_type','actor_object_id')

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True,null=True)

    target_content_type = models.ForeignKey(ContentType,related_name='target',blank=True,null=True)
    target_object_id = models.PositiveIntegerField(blank=True,null=True)
    target = generic.GenericForeignKey('target_content_type','target_object_id')

    action_object_content_type = models.ForeignKey(ContentType,related_name='action_object',blank=True,null=True)
    action_object_object_id = models.PositiveIntegerField(blank=True,null=True)
    action_object = generic.GenericForeignKey('action_object_content_type','action_object_object_id')

    timestamp = models.DateTimeField(default=datetime.now)

    public = models.BooleanField(default=True)

    objects = action_manager_class()

    def __unicode__(self):
        if self.target:
            if self.action_object:
                return u'%s %s %s on %s %s ago' % (self.actor, self.verb, self.action_object, self.target, self.timesince())
            else:
                return u'%s %s %s %s ago' % (self.actor, self.verb, self.target, self.timesince())
        return u'%s %s %s ago' % (self.actor, self.verb, self.timesince())

    def actor_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current actor
        """
        return reverse('actstream_actor', None,
                       (self.actor_content_type.pk, self.actor_object_id))

    def target_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current target
        """
        return reverse('actstream_actor', None,
                       (self.target_content_type.pk, self.target_object_id))

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the current timestamp
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    @models.permalink
    def get_absolute_url(self):
        return ('actstream.views.detail', [self.pk])

class Follow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    actor = generic.GenericForeignKey()

    objects = follow_manager_class()

    class Meta:
        unique_together = ("user", "content_type", "object_id")

    def __unicode__(self):
        return u'%s -> %s' % (self.user, self.actor)

def follow(user, actor, send_action=True):
    """
    Creates a ``User`` -> ``Actor`` follow relationship such that the actor's activities appear in the user's stream.
    Also sends the ``<user> started following <actor>`` action signal.
    Returns the created ``Follow`` instance.
    If ``send_action`` is false, no "started following" signal will be created

    Syntax::

        follow(<user>, <actor>)

    Example::

        follow(request.user, group)

    """
    follow,created = Follow.objects.get_or_create(user=user, object_id=actor.pk,
        content_type=ContentType.objects.get_for_model(actor))
    if send_action and created:
        action.send(user, verb=_('started following'), target=actor)
    return follow

def unfollow(user, actor, send_action=False):
    """
    Removes ``User`` -> ``Actor`` follow relationship.
    Optionally sends the ``<user> stopped following <actor>`` action signal.

    Syntax::

        unfollow(<user>, <actor>)

    Example::

        unfollow(request.user, other_user)

    """
    Follow.objects.filter(user = user, object_id = actor.pk,
        content_type = ContentType.objects.get_for_model(actor)).delete()
    if send_action:
        action.send(user, verb=_('stopped following'), target=actor)

def actor_stream(actor):
    return Action.objects.stream_for_actor(actor)
actor_stream.__doc__ = Action.objects.stream_for_actor.__doc__

def user_stream(user):
    return Follow.objects.stream_for_user(user)
user_stream.__doc__ = Follow.objects.stream_for_user.__doc__

def model_stream(model):
    return Action.objects.stream_for_model(model)
model_stream.__doc__ = Action.objects.stream_for_model.__doc__

def object_stream(obj):
    return Action.objects.stream_for_object(obj)
model_stream.__doc__ = Action.objects.stream_for_object.__doc__

def object_as_target_stream(obj):
    return Action.objects.stream_for_object_as_target(obj)
object_as_target_stream.__doc__ = Action.objects.stream_for_object_as_target.__doc__

def object_as_object_stream(obj):
    return Action.objects.stream_for_object_as_object(obj)
object_as_object_stream.__doc__ = Action.objects.stream_for_object_as_object.__doc__

def action_handler(verb, **kwargs):
    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')
    newaction = Action(actor_content_type = ContentType.objects.get_for_model(actor),
                    actor_object_id = actor.pk,
                    verb = unicode(verb),
                    public = bool(kwargs.pop('public', True)),
                    description = kwargs.pop('description', None),
                    timestamp = kwargs.pop('timestamp', datetime.now()))

    target = kwargs.pop('target', None)
    if target:
        newaction.target_object_id = target.pk
        newaction.target_content_type = ContentType.objects.get_for_model(target)

    action_object = kwargs.pop('action_object', None)
    if action_object:
        newaction.action_object_object_id = action_object.pk
        newaction.action_object_content_type = ContentType.objects.get_for_model(action_object)

    newaction.save()

action.connect(action_handler, dispatch_uid='actstream.models')

def delete_orphaned_actions(sender, instance, **kwargs):
    """
    When any object is deleted, delete all their actions to prevent orphans.
    """
    ctype, pk = ContentType.objects.get_for_model(instance), instance.pk
    Action.objects.filter(
        Q(action_object_object_id=pk, action_object_content_type=ctype) |
        Q(actor_object_id=pk, actor_content_type=ctype) |
        Q(target_object_id=pk, target_content_type=ctype)
    ).delete()

if getattr(settings, 'ACTSTREAM_DELETE_ORPHANED_ACTIONS', False):
    from django.db.models.signals import post_delete
    post_delete.connect(delete_orphaned_actions, dispatch_uid='actstream.models.delete')
