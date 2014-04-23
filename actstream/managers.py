from collections import defaultdict

from django.db.models import get_model
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from actstream.gfk import GFKManager
from actstream.decorators import stream


class ActionManager(GFKManager):
    """
    Default manager for Actions, accessed through Action.objects
    """

    def public(self, *args, **kwargs):
        """
        Only return public actions
        """
        kwargs['public'] = True
        return self.filter(*args, **kwargs)

    @stream
    def actor(self, object, **kwargs):
        """
        Stream of most recent actions where object is the actor.
        Keyword arguments will be passed to Action.objects.filter
        """
        return object.actor_actions.public(**kwargs)

    @stream
    def target(self, object, **kwargs):
        """
        Stream of most recent actions where object is the target.
        Keyword arguments will be passed to Action.objects.filter
        """
        return object.target_actions.public(**kwargs)

    @stream
    def action_object(self, object, **kwargs):
        """
        Stream of most recent actions where object is the action_object.
        Keyword arguments will be passed to Action.objects.filter
        """
        return object.action_object_actions.public(**kwargs)

    @stream
    def model_actions(self, model, **kwargs):
        """
        Stream of most recent actions by any particular model
        """
        ctype = ContentType.objects.get_for_model(model)
        return self.public(
            (Q(target_content_type=ctype) |
            Q(action_object_content_type=ctype) |
            Q(actor_content_type=ctype)),
            **kwargs
        )

    @stream
    def user(self, object, **kwargs):
        """
        Stream of most recent actions by objects that the passed User object is
        following.
        """
        q = Q()
        qs = self.filter(public=True)
        actors_by_content_type = defaultdict(lambda: [])
        others_by_content_type = defaultdict(lambda: [])

        follow_gfks = get_model('actstream', 'follow').objects.filter(
            user=object).values_list('content_type_id',
                                     'object_id', 'actor_only')

        if not follow_gfks:
            return qs.none()

        for content_type_id, object_id, actor_only in follow_gfks.iterator():
            actors_by_content_type[content_type_id].append(object_id)
            if not actor_only:
                others_by_content_type[content_type_id].append(object_id)

        for content_type_id, object_ids in actors_by_content_type.iteritems():
            q = q | Q(
                actor_content_type=content_type_id,
                actor_object_id__in=object_ids,
            )
        for content_type_id, object_ids in others_by_content_type.iteritems():
            q = q | Q(
                target_content_type=content_type_id,
                target_object_id__in=object_ids,
            ) | Q(
                action_object_content_type=content_type_id,
                action_object_object_id__in=object_ids,
            )
        qs = qs.filter(q, **kwargs)
        return qs


class FollowManager(GFKManager):
    """
    Manager for Follow model.
    """

    def for_object(self, instance):
        """
        Filter to a specific instance.
        """
        content_type = ContentType.objects.get_for_model(instance).pk
        return self.filter(content_type=content_type, object_id=instance.pk)

    def is_following(self, user, instance):
        """
        Check if a user is following an instance.
        """
        if not user or user.is_anonymous():
            return False
        queryset = self.for_object(instance)
        return queryset.filter(user=user).exists()

    def followers(self, actor, verbs=()):
        """
        Returns a list of User objects who are following the given actor
        (eg my followers) for one or several given verbs (optional).
        """

        if not hasattr(verbs, '__iter__'):
            verbs = [verbs]

        l = []
        for follow in self.filter(
            content_type=ContentType.objects.get_for_model(actor),
            object_id=actor.pk,
        ).select_related('user'):
            u = follow.user
            if not follow.verbs or follow.verbs.intersection(verbs):
                l.append(u)
        return l

    def following(self, user, *models, **kwargs):
        """
        Returns a list of actors that the given user is following (eg who i'm
        following). Items in the list can be of any model unless a list of
        restricted models is passed.
        Eg following(user, User) will only return users following the given user
        If one or several verbs are passed using keyword ``verbs``, this
        returns only objects followed using these verbs
        """
        verbs = kwargs.pop('verbs', [])
        if not hasattr(verbs, '__iter__'):
            verbs = [verbs]

        qs = self.filter(user=user)
        if len(models):
            qs = qs.filter(content_type__in=(
                ContentType.objects.get_for_model(model) for model in models)
            )
        l = []
        for follow in qs.fetch_generic_relations():
            o = follow.follow_object
            if not follow.verbs or follow.verbs.intersection(verbs):
                l.append(o)
        return l
