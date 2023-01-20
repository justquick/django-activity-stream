
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist

from actstream import settings
from actstream.signals import action
from actstream.registry import check


def follow(user, obj, send_action=True, actor_only=True, flag='', **kwargs):
    """
    Creates a relationship allowing the object's activities to appear in the
    user's stream.

    Returns the created ``Follow`` instance.

    If ``send_action`` is ``True`` (the default) then a
    ``<user> started following <object>`` action signal is sent.
    Kwargs that can be passed to the Follow model instance will be passed.
    Extra keyword arguments are passed to the action.send call.

    If ``actor_only`` is ``True`` (the default) then only actions where the
    object is the actor will appear in the user's activity stream. Set to
    ``False`` to also include actions where this object is the action_object or
    the target.

    If ``flag`` not an empty string then the relationship would marked by this flag.

    Example::

        follow(request.user, group, actor_only=False)
        follow(request.user, group, actor_only=False, flag='liking')
    """
    check(obj)
    follow_model = settings.get_follow_model()
    instance, created = follow_model.objects.get_or_create(
        user=user, object_id=obj.pk, flag=flag,
        content_type=ContentType.objects.get_for_model(obj),
        actor_only=actor_only
    )
    follow_updated = False
    for attr in list(kwargs):
        try:
            follow_model._meta.get_field(attr)
        except FieldDoesNotExist:
            pass
        else:
            follow_updated = True
            setattr(instance, attr, kwargs.pop(attr))
    if follow_updated:
        instance.save()
    if send_action and created:
        if not flag:
            action.send(user, verb=_('started following'), target=obj, **kwargs)
        else:
            action.send(user, verb=_('started %s' % flag), target=obj, **kwargs)
    return instance


def unfollow(user, obj, send_action=False, flag=''):
    """
    Removes a "follow" relationship.

    Set ``send_action`` to ``True`` (``False is default) to also send a
    ``<user> stopped following <object>`` action signal.

    Pass a string value to ``flag`` to determine which type of "follow" relationship you want to remove.

    Example::

        unfollow(request.user, other_user)
        unfollow(request.user, other_user, flag='watching')
    """
    check(obj)
    qs = settings.get_follow_model().objects.filter(
        user=user, object_id=obj.pk,
        content_type=ContentType.objects.get_for_model(obj)
    )

    if flag:
        qs = qs.filter(flag=flag)
    qs.delete()

    if send_action:
        if not flag:
            action.send(user, verb=_('stopped following'), target=obj)
        else:
            action.send(user, verb=_('stopped %s' % flag), target=obj)


def is_following(user, obj, flag=''):
    """
    Checks if a "follow" relationship exists.

    Returns True if exists, False otherwise.

    Pass a string value to ``flag`` to determine which type of "follow" relationship you want to check.

    Example::

        is_following(request.user, group)
        is_following(request.user, group, flag='liking')
    """
    check(obj)

    qs = settings.get_follow_model().objects.filter(
        user=user, object_id=obj.pk,
        content_type=ContentType.objects.get_for_model(obj)
    )

    if flag:
        qs = qs.filter(flag=flag)

    return qs.exists()


def action_handler(verb, **kwargs):
    """
    Handler function to create Action instance upon action signal call.
    Extra kwargs will be passed to the Action instance
    """
    kwargs.pop('signal', None)
    actor = kwargs.pop('sender')

    # We must store the untranslated string
    # If verb is an ugettext_lazyed string, fetch the original string
    if hasattr(verb, '_proxy____args'):
        verb = verb._proxy____args[0]

    newaction = settings.get_action_model()(
        actor_content_type=ContentType.objects.get_for_model(actor),
        actor_object_id=actor.pk,
        verb=str(verb),
        public=bool(kwargs.pop('public', True)),
        description=kwargs.pop('description', None),
        timestamp=kwargs.pop('timestamp', now())
    )

    for opt in ('target', 'action_object'):
        obj = kwargs.pop(opt, None)
        if obj is not None:
            check(obj)
            setattr(newaction, '%s_object_id' % opt, obj.pk)
            setattr(newaction, '%s_content_type' % opt,
                    ContentType.objects.get_for_model(obj))
    for attr in list(kwargs):
        try:
            settings.get_action_model()._meta.get_field(attr)
        except FieldDoesNotExist:
            pass
        else:
            setattr(newaction, attr, kwargs.pop(attr))
    if settings.USE_JSONFIELD and len(kwargs):
        newaction.data = kwargs
    newaction.save(force_insert=True)
    return newaction
