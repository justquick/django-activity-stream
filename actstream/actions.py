import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from actstream.exceptions import check_actionable_model
from actstream import settings

try:
    from django.utils import timezone
    now = timezone.now
except ImportError:
    now = datetime.datetime.now


def follow(user, obj, send_action=True, actor_only=True, verbs=None):
    """
    Creates a relationship allowing the object's activities to appear in the
    user's stream.

    Returns the created ``Follow`` instance.

    If ``send_action`` is ``True`` (the default) then a
    ``<user> started following <object>`` action signal is sent.

    If ``actor_only`` is ``True`` (the default) then only actions where the
    object is the actor will appear in the user's activity stream. Set to
    ``False`` to also include actions where this object is the action_object or
    the target.

    If ``verbs`` is defined as a string or a tuple, only actions bearing
    this or these verb(s) will appear in the user's activity stream. If
    ``verbs`` is None, all actions will appear in the stream

    Example::

        follow(request.user, group, actor_only=False)
    """
    from actstream.models import Follow, action

    if verbs:
        if hasattr(verbs, '__iter__'):
            verbs = set(verbs)
        else:
            # transforms a string in a single-item list
            verbs = set([verbs])

    check_actionable_model(obj)
    follow, created = Follow.objects.get_or_create(user=user,
        object_id=obj.pk,
        content_type=ContentType.objects.get_for_model(obj)
    )

    save_follow = False
    # update actor_only
    if follow.actor_only != actor_only:
        follow.actor_only = actor_only
        save_follow = True

    # update verbs
    if verbs:
        follow.verbs = verbs
        save_follow = True

    # save if necessary
    if save_follow:
        follow.save()

    if send_action and created:
        action.send(user, verb=_('started following'), target=obj)

    return follow


def unfollow(user, obj, send_action=False, verbs=None):
    """
    Removes a "follow" relationship.

    Set ``send_action`` to ``True`` (``False is default) to also send a
    ``<user> stopped following <object>`` action signal.

    If ``verbs`` is defined as a string or a tuple, only actions bearing this
    or these verbs will be removed from this user's activity stream.
    If ``verbs`` is None, no action will longer appear in the stream

    Example::

        unfollow(request.user, other_user)
    """
    from actstream.models import Follow, action

    check_actionable_model(obj)

    follow_obj = Follow.objects.filter(user=user, object_id=obj.pk,
        content_type=ContentType.objects.get_for_model(obj))

    if verbs is None:
        # easy, just delete the Follow instance
        follow_obj.delete()
    else:
        if not hasattr(verbs, '__iter__'):  # excludes strings, that's wanted
            verbs = [verbs]

        # remove verbs
        follow_obj.verbs.difference_update(verbs)

        # if there is no more verb to follow, delete the Follow object
        if not follow_obj.verbs:
            follow_obj.delete()
        else:
            follow_obj.save()

    if send_action:
        action.send(user, verb=_('stopped following'), target=obj)


def is_following(user, obj):
    """
    Checks if a "follow" relationship exists.

    Returns True if exists, False otherwise.

    Example::

        is_following(request.user, group)
    """
    from actstream.models import Follow

    check_actionable_model(obj)
    return bool(Follow.objects.filter(user=user, object_id=obj.pk,
        content_type=ContentType.objects.get_for_model(obj)).count())


def action_handler(verb, **kwargs):
    """
    Handler function to create Action instance upon action signal call.
    """
    from actstream.models import Action

    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')
    check_actionable_model(actor)

    # We must store the unstranslated string
    # If verb is an ugettext_lazyed string, fetch the original string
    if hasattr(verb, '_proxy____args'):
        verb = verb._proxy____args[0]

    newaction = Action(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=unicode(verb),
        public=bool(kwargs.pop('public', True)),
        description=kwargs.pop('description', None),
        timestamp=kwargs.pop('timestamp', now())
    )

    for opt in ('target', 'action_object'):
        obj = kwargs.pop(opt, None)
        if not obj is None:
            check_actionable_model(obj)
            setattr(newaction, '%s_object_id' % opt, obj.pk)
            setattr(newaction, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))
    if settings.USE_JSONFIELD and len(kwargs):
        newaction.data = kwargs
    newaction.save()
