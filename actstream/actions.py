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


def follow(user, obj, send_action=True, actor_only=True):
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

    Example::

        follow(request.user, group, actor_only=False)
    """
    from actstream.models import Follow, action

    check_actionable_model(obj)
    follow, created = Follow.objects.get_or_create(user=user,
        object_id=obj.pk,
        content_type=ContentType.objects.get_for_model(obj),
        actor_only=actor_only)
    if send_action and created:
        action.send(user, verb=_('started following'), target=obj)
    return follow


def unfollow(user, obj, send_action=False):
    """
    Removes a "follow" relationship.

    Set ``send_action`` to ``True`` (``False is default) to also send a
    ``<user> stopped following <object>`` action signal.

    Example::

        unfollow(request.user, other_user)
    """
    from actstream.models import Follow, action

    check_actionable_model(obj)
    Follow.objects.filter(user=user, object_id=obj.pk,
        content_type=ContentType.objects.get_for_model(obj)).delete()
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
