from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext as _
from django.utils.timesince import timesince as djtimesince
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.timezone import now

from actstream import settings as actstream_settings
from actstream.managers import FollowManager


class AbstractFollow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, db_index=True
    )
    object_id = models.CharField(max_length=255, db_index=True)
    follow_object = GenericForeignKey()
    actor_only = models.BooleanField(
        "Only follow actions where "
        "the object is the target.",
        default=True
    )
    flag = models.CharField(max_length=255, blank=True, db_index=True, default='')
    started = models.DateTimeField(default=now, db_index=True)
    objects = FollowManager()

    class Meta:
        abstract = True
        unique_together = ('user', 'content_type', 'object_id', 'flag')

    def __str__(self):
        return '{} -> {} : {}'.format(self.user, self.follow_object, self.flag)


class AbstractAction(models.Model):
    """
    Action model describing the actor acting out a verb (on an optional
    target).
    Nomenclature based on http://activitystrea.ms/specs/atom/1.0/

    Generalized Format::

        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::

        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <about 2 hours ago>

    Unicode Representation::

        justquick reached level 60 1 minute ago
        mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

    HTML Representation::

        <a href="http://oebfare.com/">brosner</a> commented on <a href="http://github.com/pinax/pinax">pinax/pinax</a> 2 hours ago

    """
    actor_content_type = models.ForeignKey(
        ContentType, related_name='%(app_label)s_actor',
        on_delete=models.CASCADE, db_index=True
    )
    actor_object_id = models.CharField(max_length=255, db_index=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        related_name='%(app_label)s_target',
        on_delete=models.CASCADE, db_index=True
    )
    target_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    target = GenericForeignKey(
        'target_content_type',
        'target_object_id'
    )

    action_object_content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        related_name='%(app_label)s_action_object',
        on_delete=models.CASCADE, db_index=True
    )
    action_object_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    action_object = GenericForeignKey(
        'action_object_content_type',
        'action_object_object_id'
    )

    timestamp = models.DateTimeField(default=now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)

    objects = actstream_settings.get_action_manager()

    class Meta:
        abstract = True
        ordering = ('-timestamp',)

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'target': self.target,
            'timesince': self.timesince()
        }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago') % ctx
            return _('%(actor)s %(verb)s %(target)s %(timesince)s ago') % ctx
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(timesince)s ago') % ctx
        return _('%(actor)s %(verb)s %(timesince)s ago') % ctx

    def actor_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current actor.
        """
        return reverse('actstream_actor', None,
                       (self.actor_content_type.pk, self.actor_object_id))

    def target_url(self):
        """
        Returns the URL to the ``actstream_actor`` view for the current target.
        """
        return reverse('actstream_actor', None,
                       (self.target_content_type.pk, self.target_object_id))

    def action_object_url(self):
        """
        Returns the URL to the ``actstream_action_object`` view for the current action object
        """
        return reverse('actstream_actor', None, (
            self.action_object_content_type.pk, self.action_object_object_id))

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        return djtimesince(self.timestamp, now).encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8')

    def get_absolute_url(self):
        return reverse(
            'actstream_detail', args=[self.pk])


class Follow(AbstractFollow):
    class Meta(AbstractFollow.Meta):
        swappable = 'ACTSTREAM_FOLLOW_MODEL'


class Action(AbstractAction):
    class Meta(AbstractAction.Meta):
        swappable = 'ACTSTREAM_ACTION_MODEL'


# convenient accessors
actor_stream = actstream_settings.get_action_model().objects.actor
action_object_stream = actstream_settings.get_action_model().objects.action_object
target_stream = actstream_settings.get_action_model().objects.target
user_stream = actstream_settings.get_action_model().objects.user
model_stream = actstream_settings.get_action_model().objects.model_actions
any_stream = actstream_settings.get_action_model().objects.any
followers = actstream_settings.get_follow_model().objects.followers
following = actstream_settings.get_follow_model().objects.following
