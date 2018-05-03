from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timesince import timesince as djtimesince
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from actstream import get_action_model, get_follow_model
from actstream import settings as actstream_settings
from actstream.managers import FollowManager


@python_2_unicode_compatible
class AbstractFollow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_follows",
        related_query_name="%(app_label)s_%(class)s_follows"
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_follow_objects",
        related_query_name="%(app_label)s_%(class)s_follow_objects"
    )
    object_id = models.CharField(max_length=255, db_index=True)
    follow_object = GenericForeignKey()
    actor_only = models.BooleanField(
        "Only follow actions where the object is the target.",
        default=True
    )
    flag = models.CharField(max_length=255, blank=True, db_index=True, default='')
    started = models.DateTimeField(default=now, db_index=True)
    objects = FollowManager()

    class Meta:
        abstract = True
        unique_together = ('user', 'content_type', 'object_id', 'flag')

    def __str__(self):
        return '%s -> %s : %s' % (self.user, self.follow_object, self.flag)


@python_2_unicode_compatible
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
        ContentType,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_actors",
        related_query_name="%(app_label)s_%(class)s_actors"
    )
    actor_object_id = models.CharField(max_length=255, db_index=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_targets",
        related_query_name="%(app_label)s_%(class)s_targets"
    )
    target_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    target = GenericForeignKey(
        'target_content_type',
        'target_object_id'
    )

    action_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_action_objects",
        related_query_name="%(app_label)s_%(class)s_action_objects"
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
        Return the URL to the ``actstream_actor`` view for the current actor.
        """
        return reverse('actstream_actor', None,
                       (self.actor_content_type.pk, self.actor_object_id))

    def target_url(self):
        """
        Return the URL to the ``actstream_actor`` view for the current target.
        """
        return reverse('actstream_actor', None,
                       (self.target_content_type.pk, self.target_object_id))

    def action_object_url(self):
        """
        Return the URL to the ``actstream_action_object`` view for the current action object.
        """
        return reverse('actstream_actor', None, (
            self.action_object_content_type.pk, self.action_object_object_id))

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the current timestamp.
        """
        return djtimesince(self.timestamp, now).encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8')

    def get_absolute_url(self):
        return reverse(
            'actstream.views.detail', [self.pk])


class Follow(AbstractFollow):
    class Meta(AbstractFollow.Meta):
        swappable = 'ACTSTREAM_FOLLOW_MODEL'


class Action(AbstractAction):
    class Meta(AbstractAction.Meta):
        swappable = 'ACTSTREAM_ACTION_MODEL'


# convenient accessors
actor_stream = get_action_model().objects.actor
action_object_stream = get_action_model().objects.action_object
target_stream = get_action_model().objects.target
user_stream = get_action_model().objects.user
model_stream = get_action_model().objects.model_actions
any_stream = get_action_model().objects.any
followers = get_follow_model().objects.followers
following = get_follow_model().objects.following
