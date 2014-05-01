from collections import defaultdict

from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.template.base import Context

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    from datetime import datetime
    now = datetime.now

from actstream import settings as actstream_settings
from actstream.signals import action
from actstream.actions import action_handler
from actstream.managers import FollowManager
from actstream.compat import user_model_label

User = user_model_label

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
    actor_content_type = models.ForeignKey(ContentType, related_name='actor')
    actor_object_id = models.CharField(max_length=255)
    actor = generic.GenericForeignKey('actor_content_type', 'actor_object_id')

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    target_content_type = models.ForeignKey(ContentType, related_name='target',
        blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = generic.GenericForeignKey('target_content_type',
        'target_object_id')

    action_object_content_type = models.ForeignKey(ContentType,
        related_name='action_object', blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255, blank=True,
        null=True)
    action_object = generic.GenericForeignKey('action_object_content_type',
        'action_object_object_id')

    timestamp = models.DateTimeField(default=now)

    public = models.BooleanField(default=True)

    objects = actstream_settings.get_action_manager()

    class Meta:
        ordering = ('-timestamp',)

    def __unicode__(self):
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
        return reverse('actstream_actor', None,
            (self.action_object_content_type.pk, self.action_object_object_id))

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.timestamp, now)

    @models.permalink
    def get_absolute_url(self):
        return ('actstream.views.detail', [self.pk])

    def _render(self, context, **kwargs):
        """
        Renders the action from a template
        """

        dic = dict(kwargs, action=self)

        user = kwargs.get('user', None) or context.get('user', None)
        if user and 'unread' not in dic:
            dic['unread'] = self.is_unread(user)

        data = getattr(self, 'data', None)
        if data:
            dic.update(data)

        norm_verb = self.verb.replace(' ', '_')
        templates = [
            'actstream/%s/action.html' % norm_verb,
            'actstream/action.html',
            'activity/%s/action.html' % norm_verb,
            'activity/action.html',
        ]
        return render_to_string(templates, dic, context)

    def unread_in_qs(self, user):
        """
        Cache the queryset of Follow objects for which the action is unread
        for that user
        """
        if not hasattr(self, '_unread_in_qs'):
            self._unread_in_qs = {}
        qs = self._unread_in_qs.get(user.id, None)
        if qs is None:
            self._unread_in_qs[user.id] = qs = self.unread_in.filter(user=user)
        return qs

    def reset_unread_in_cache(self, user=None):
        if user:
            if not hasattr(self, '_unread_in_qs'):
                self._unread_in_qs = {}
            self._unread_in_qs[user.id] = self.unread_in.filter(user=user)
        else:
            self._unread_in_qs = {}

    def is_unread(self, user):
        """
        Returns True if the action is unread for that user
        """
        if self.unread_in_qs(user).count():
            return True
        return False

    def mark_read(self, user, force=False, commit=True):
        """
        Attempts to mark the action as read using the follow objects' mark_read
        method. Returns True if the action was unread before
        If you want to mark several actions as read, prefer the classmethod
        bulk_mark_read
        """
        unread = False
        for follow in self.unread_in_qs(user):
            unread = True
            follow.mark_read((self,), force, commit)
        # update cached queryset
        self.reset_unread_in_cache(user)
        return unread

    def render(self, context, commit=True, **kwargs):
        """
        Renders the action, attempting to mark it as read if user is not None
        Returns a rendered string
        """

        user = kwargs.get('user', None) or context.get('user', None)
        if user and not 'unread' in kwargs:
            kwargs['unread'] = self.mark_read(user, commit=commit)
        return self._render(context, **kwargs)

    @classmethod
    def bulk_is_read(cls, user, actions):
        """
        Does not bring any performance gains over Action.is_read method, exists
        for the sake of consistency with bulk_mark_read and bulk_render
        """
        unread = []
        for a in actions:
            unread.append(a.is_unread())

    @classmethod
    def bulk_mark_read(cls, user, actions, force=False, commit=True):
        """
        Marks a list or queryset of actions as read for the given user
        It is more efficient than calling the mark_read method on each action,
        especially if many actions belong to only a few followers

        Returns a list ``l`` of boolean. If ``actions[i]`` was unread before
        the call to bulk_mark_read, ``l[i]`` is True
        """

        follow_dict = defaultdict(lambda: [])
        unread = []
        for a in actions:
            urd = False  # unread marker
            for f in a.unread_in_qs(user):
                follow_dict[f].append(a)
                urd = True
            unread.append(urd)

        for follow, actions in follow_dict.iteritems():
            follow.mark_read(actions, force, commit)

        # update cached querysets
        for a in actions:
            a.reset_unread_in_cache(user)

        return unread

    @classmethod
    def bulk_render(cls, actions=(), user=None, commit=True, **kwargs):
        """
        Renders a list or queryset of actions, returning a list of rendered
        strings in the same order as ``actions``

        If ``user`` is provided, the class method will attempt to mark the
        actions as read for the user using Action.mark_read above
        """

        if user:
            kwargs['user'] = user

        unread = kwargs.pop('unread', None)
        if unread is None and user:
            unread = cls.bulk_mark_read(user, actions, commit=commit)
        else:
            # do not care about using count(), if actions is a queryset it
            # needs to be evaluated at the next step anyway
            unread = [unread] * len(action)

        rendered = []
        for a, urd in zip(actions, unread):
            rendered.append(a._render(Context(), unread=urd, **kwargs))
        return rendered


class Follow(models.Model):
    """
    Lets a user follow the activities of any specific actor
    """
    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=255)
    follow_object = generic.GenericForeignKey()
    actor_only = models.BooleanField("Only follow actions where the object is "
        "the target.", default=True)
    started = models.DateTimeField(default=now)
    last_updated = models.DateTimeField(default=now)
    objects = FollowManager()

    # unread Actions tracking
    track_unread = models.BooleanField(
        default=actstream_settings.TRACK_UNREAD_DEFAULT)
    auto_read = models.BooleanField(
        default=actstream_settings.AUTO_READ_DEFAULT)
    unread_actions = models.ManyToManyField(Action, related_name='unread_in')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __unicode__(self):
        return u'%s -> %s' % (self.user, self.follow_object)

    def update_unread(self, qs=None):
        """
        Returns a queryset of the unread actions after having extracted the
        latest actions from the ``qs`` and updated ``self.unread_actions``
        """

        if self.track_unread:
            if qs is None:
                qs = Action.objects.follow(self)
            # get actions that occured since the last time the Follow object
            # was fetched and update unread_actions
            last_actions = qs.filter(timestamp__gte=self.last_updated)
            self.unread_actions.add(*last_actions)
            for a in last_actions:
                a.reset_unread_in_cache()

        self.last_updated = now()
        self.save()
        return self.unread_actions.all()

    def mark_read(self, actions, force=False, commit=True):
        """
        Marks an iterable of Action objects as read. This removes them from
        the unread_actions queryset

        If ``force`` is set to True, the actions will be marked as unread no
        matter the value of self.auto_read.
        """
        if force or self.auto_read:
            # We don't care if some actions are not in unread_actions
            self.unread_actions.remove(*actions)
            if commit:
                self.save()


# convenient accessors
actor_stream = Action.objects.actor
action_object_stream = Action.objects.action_object
target_stream = Action.objects.target
user_stream = Action.objects.user
model_stream = Action.objects.model_actions
followers = Follow.objects.followers
following = Follow.objects.following


def setup_generic_relations():
    """
    Set up GenericRelations for actionable models.
    """
    for model in actstream_settings.get_models().values():
        if not model:
            continue
        for field in ('actor', 'target', 'action_object'):
            attr = '%s_actions' % field
            if isinstance(getattr(model, attr, None),
                          generic.ReverseGenericRelatedObjectsDescriptor):
                break
            generic.GenericRelation(Action,
                content_type_field='%s_content_type' % field,
                object_id_field='%s_object_id' % field,
                related_name='actions_with_%s_%s_as_%s' % (
                    model._meta.app_label, model._meta.module_name, field),
            ).contribute_to_class(model, attr)

            # @@@ I'm not entirely sure why this works
            setattr(Action, 'actions_with_%s_%s_as_%s' % (
                model._meta.app_label, model._meta.module_name, field), None)


setup_generic_relations()


if actstream_settings.USE_JSONFIELD:
    try:
        from jsonfield.fields import JSONField
    except ImportError:
        raise ImproperlyConfigured('You must have django-jsonfield installed '
                                'if you wish to use a JSONField on your actions')
    JSONField(blank=True, null=True).contribute_to_class(Action, 'data')

# connect the signal
action.connect(action_handler, dispatch_uid='actstream.models')
