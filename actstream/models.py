from __future__ import unicode_literals

import django
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timesince import timesince as djtimesince
from django.contrib.contenttypes.models import ContentType

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    from datetime import datetime
    now = datetime.now

from actstream import settings as actstream_settings
from actstream.managers import FollowManager
from actstream.compat import user_model_label, generic


@python_2_unicode_compatible
class Follow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(
        user_model_label, on_delete=models.CASCADE, db_index=True
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, db_index=True
    )
    object_id = models.CharField(max_length=255, db_index=True)
    follow_object = generic.GenericForeignKey()
    actor_only = models.BooleanField(
        "Only follow actions where "
        "the object is the target.",
        default=True
    )
    started = models.DateTimeField(default=now, db_index=True)
    objects = FollowManager()

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return '%s -> %s' % (self.user, self.follow_object)


@python_2_unicode_compatible
class Action(models.Model):
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
        ContentType, related_name='actor',
        on_delete=models.CASCADE, db_index=True
    )
    actor_object_id = models.CharField(max_length=255, db_index=True)
    actor = generic.GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        related_name='target',
        on_delete=models.CASCADE, db_index=True
    )
    target_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    target = generic.GenericForeignKey('target_content_type',
                                       'target_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        related_name='action_object',
        on_delete=models.CASCADE, db_index=True
    )
    action_object_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    action_object = generic.GenericForeignKey('action_object_content_type',
                                              'action_object_object_id')

    timestamp = models.DateTimeField(default=now, db_index=True)

    public = models.BooleanField(default=True, db_index=True)

    objects = actstream_settings.get_action_manager()

    class Meta:
        ordering = ('-timestamp', )

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

    @models.permalink
    def get_absolute_url(self):
        return 'actstream.views.detail', [self.pk]


# convenient accessors
actor_stream = Action.objects.actor
action_object_stream = Action.objects.action_object
target_stream = Action.objects.target
user_stream = Action.objects.user
model_stream = Action.objects.model_actions
any_stream = Action.objects.any
followers = Follow.objects.followers
following = Follow.objects.following
