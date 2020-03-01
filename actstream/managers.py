from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


from actstream.gfk import GFKManager
from actstream.decorators import stream
from actstream.registry import check


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
    def user(self, obj, with_user_activity=False, follow_flag=None, **kwargs):
        """Create a stream of the most recent actions by objects that the user is following."""
        q = Q()
        qs = self.public()

        if not obj:
            return qs.none()

        check(obj)

        if with_user_activity:
            q = q | Q(
                actor_content_type=ContentType.objects.get_for_model(obj),
                actor_object_id=obj.pk
            )

        follows = apps.get_model('actstream', 'follow').objects.filter(user=obj)
        if follow_flag:
            follows = follows.filter(flag=follow_flag)
            
        content_types = ContentType.objects.filter(
            pk__in=follows.values('content_type_id')
        )

        if not (content_types.exists() or with_user_activity):
            return qs.none()

        for content_type in content_types:
            object_ids = follows.filter(content_type=content_type)
            q = q | Q(
                actor_content_type=content_type,
                actor_object_id__in=object_ids.values('object_id')
            ) | Q(
                target_content_type=content_type,
                target_object_id__in=object_ids.filter(
                    actor_only=False).values('object_id')
            ) | Q(
                action_object_content_type=content_type,
                action_object_object_id__in=object_ids.filter(
                    actor_only=False).values('object_id')
            )

        return qs.filter(q, **kwargs)


class FollowManager(GFKManager):
    """
    Manager for Follow model.
    """

    def for_object(self, instance, flag=''):
        """
        Filter to a specific instance.
        """
        check(instance)
        content_type = ContentType.objects.get_for_model(instance).pk
        queryset = self.filter(content_type=content_type, object_id=instance.pk)
        if flag:
            queryset = queryset.filter(flag=flag)
        return queryset

    def is_following(self, user, instance, flag=''):
        """
        Check if a user is following an instance.
        """
        if not user or user.is_anonymous:
            return False
        queryset = self.for_object(instance)

        if flag:
            queryset = queryset.filter(flag=flag)
        return queryset.filter(user=user).exists()

    def followers_qs(self, actor, flag=''):
        """
        Returns a queryset of User objects who are following the given actor (eg my followers).
        """
        check(actor)
        queryset = self.filter(
            content_type=ContentType.objects.get_for_model(actor),
            object_id=actor.pk
        ).select_related('user')

        if flag:
            queryset = queryset.filter(flag=flag)
        return queryset

    def followers(self, actor, flag=''):
        """
        Returns a list of User objects who are following the given actor (eg my followers).
        """
        return [follow.user for follow in self.followers_qs(actor, flag=flag)]

    def following_qs(self, user, *models, **kwargs):
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

        flag = kwargs.get('flag', '')

        if flag:
            qs = qs.filter(flag=flag)
        return qs.fetch_generic_relations('follow_object')

    def following(self, user, *models, **kwargs):
        """
        Returns a list of actors that the given user is following (eg who im following).
        Items in the list can be of any model unless a list of restricted models are passed.
        Eg following(user, User) will only return users following the given user
        """
        return [follow.follow_object for follow in self.following_qs(
            user, *models, flag=kwargs.get('flag', '')
        )]
