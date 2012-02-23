from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from actstream.exceptions import check_actionable_model


def follow(user, actor, send_action=True):
    """
    Creates a ``User`` -> ``Actor`` follow relationship such that the actor's
    activities appear in the user's stream.
    Also sends the ``<user> started following <actor>`` action signal.
    Returns the created ``Follow`` instance.
    If ``send_action`` is false, no "started following" signal will be created

    Syntax::

        follow(<user>, <actor>)

    Example::

        follow(request.user, group)

    """
    from actstream.models import Follow, action

    check_actionable_model(actor)
    follow, created = Follow.objects.get_or_create(user=user,
        object_id=actor.pk,
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
    from actstream.models import Follow, action

    check_actionable_model(actor)
    Follow.objects.filter(user=user, object_id=actor.pk,
        content_type=ContentType.objects.get_for_model(actor)).delete()
    if send_action:
        action.send(user, verb=_('stopped following'), target=actor)


def is_following(user, actor):
    """
    Checks if a ``User`` -> ``Actor`` relationship exists.
    Returns True if exists, False otherwise.

    Syntax::

        is_following(<user>, <actor>)

    Example::

        is_following(request.user, group)

    """
    from actstream.models import Follow

    check_actionable_model(actor)
    return bool(Follow.objects.filter(user=user, object_id=actor.pk,
        content_type=ContentType.objects.get_for_model(actor)).count())


def action_handler(verb, **kwargs):
    """
    Handler function to create Action instance upon action signal call.
    """
    from actstream.models import Action

    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')
    check_actionable_model(actor)
    newaction = Action(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=unicode(verb),
        public=bool(kwargs.pop('public', True)),
        description=kwargs.pop('description', None),
        timestamp=kwargs.pop('timestamp', datetime.now())
    )

    for opt in ('target', 'action_object'):
        obj = kwargs.pop(opt, None)
        if not obj is None:
            check_actionable_model(obj)
            setattr(newaction, '%s_object_id' % opt, obj.pk)
            setattr(newaction, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))

    newaction.save()