from collections import defaultdict

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from actstream.gfk import GFKManager
from actstream.decorators import stream
from actstream.registry import check
from actstream.compat import get_model


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
    def actor(self, obj, **kwargs):
        """
        Stream of most recent actions where obj is the actor.
        Keyword arguments will be passed to Action.objects.filter
        """
        check(obj)
        return obj.actor_actions.public(**kwargs)

    @stream
    def target(self, obj, **kwargs):
        """
        Stream of most recent actions where obj is the target.
        Keyword arguments will be passed to Action.objects.filter
        """
        check(obj)
        return obj.target_actions.public(**kwargs)

    @stream
    def action_object(self, obj, **kwargs):
        """
        Stream of most recent actions where obj is the action_object.
        Keyword arguments will be passed to Action.objects.filter
        """
        check(obj)
        return obj.action_object_actions.public(**kwargs)

    @stream
    def model_actions(self, model, **kwargs):
        """
        Stream of most recent actions by any particular model
        """
        check(model)
        ctype = ContentType.objects.get_for_model(model)
        return self.public(
            (Q(target_content_type=ctype) |
             Q(action_object_content_type=ctype) |
             Q(actor_content_type=ctype)),
            **kwargs
        )

    @stream
    def any(self, obj, **kwargs):
        """
        Stream of most recent actions where obj is the actor OR target OR action_object.
        """
        check(obj)
        ctype = ContentType.objects.get_for_model(obj)
        return self.public(
            Q(
                actor_content_type=ctype,
                actor_object_id=obj.pk,
            ) | Q(
                target_content_type=ctype,
                target_object_id=obj.pk,
            ) | Q(
                action_object_content_type=ctype,
                action_object_object_id=obj.pk,
            ), **kwargs)

    @stream
    def user(self, obj, **kwargs):
        """
        Stream of most recent actions by objects that the passed User obj is
        following.
        """
        q = Q()
        qs = self.public()

        if not obj:
            return qs.none()

        check(obj)
        actors_by_content_type = defaultdict(lambda: [])
        others_by_content_type = defaultdict(lambda: [])

        if kwargs.pop('with_user_activity', False):
            object_content_type = ContentType.objects.get_for_model(obj)
            actors_by_content_type[object_content_type.id].append(obj.pk)

        follow_gfks = get_model('actstream', 'follow').objects.filter(
            user=obj).values_list('content_type_id',
                                  'object_id', 'actor_only')

        for content_type_id, object_id, actor_only in follow_gfks.iterator():
            actors_by_content_type[content_type_id].append(object_id)
            if not actor_only:
                others_by_content_type[content_type_id].append(object_id)

        if len(actors_by_content_type) + len(others_by_content_type) == 0:
            return qs.none()

        for content_type_id, object_ids in actors_by_content_type.items():
            q = q | Q(
                actor_content_type=content_type_id,
                actor_object_id__in=object_ids,
            )
        for content_type_id, object_ids in others_by_content_type.items():
            q = q | Q(
                target_content_type=content_type_id,
                target_object_id__in=object_ids,
            ) | Q(
                action_object_content_type=content_type_id,
                action_object_object_id__in=object_ids,
            )
        return qs.filter(q, **kwargs)


class FollowManager(GFKManager):
    """
    Manager for Follow model.
    """

    def for_object(self, instance):
        """
        Filter to a specific instance.
        """
        check(instance)
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

    def followers_qs(self, actor):
        """
        Returns a queryset of User objects who are following the given actor (eg my followers).
        """
        check(actor)
        return self.filter(
            content_type=ContentType.objects.get_for_model(actor),
            object_id=actor.pk
        ).select_related('user')

    def followers(self, actor):
        """
        Returns a list of User objects who are following the given actor (eg my followers).
        """
        return [follow.user for follow in self.followers_qs(actor)]

    def following_qs(self, user, *models):
        """
        Returns a queryset of actors that the given user is following (eg who im following).
        Items in the list can be of any model unless a list of restricted models are passed.
        Eg following(user, User) will only return users following the given user
        """
        qs = self.filter(user=user)
        ctype_filters = Q()
        for model in models:
            check(model)
            ctype_filters |= Q(content_type=ContentType.objects.get_for_model(model))
        qs = qs.filter(ctype_filters)
        return qs.fetch_generic_relations('follow_object')

    def following(self, user, *models):
        """
        Returns a list of actors that the given user is following (eg who im following).
        Items in the list can be of any model unless a list of restricted models are passed.
        Eg following(user, User) will only return users following the given user
        """
        return [follow.follow_object for follow in self.following_qs(user, *models)]
