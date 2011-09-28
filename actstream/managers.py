from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
        
class ActionManager(models.Manager):
    def stream_for_actor(self, actor):
        """
        Produces a QuerySet of most recent activities for any actor
        """
        return self.filter(
            actor_content_type = ContentType.objects.get_for_model(actor),
            actor_object_id = actor.pk,
        ).order_by('-timestamp')

    def stream_for_model(self, model):
        """
        Produces a QuerySet of most recent activities for any model
        """
        return self.filter(
            Q(target_content_type = ContentType.objects.get_for_model(model)) |
            Q(action_object_content_type = ContentType.objects.get_for_model(model))
        ).order_by('-timestamp')

    def stream_for_object(self, obj):
        """
        Produces a QuerySet of most recent activities where the model is the object
        of the action
        """
        return self.filter(
            Q(target_object_id = obj.id) |
            Q(action_object_object_id = obj.id)
        ).order_by('-timestamp')

    def stream_for_object_as_object(self, obj):
        """
        Produces a QuerySet of most recent activities where the model is the object
        of the action
        """
        return self.filter(
            action_object_object_id = obj.id
        ).order_by('-timestamp')

    def stream_for_object_as_target(self, obj):
        """
        Produces a QuerySet of most recent activities where the object is the target
        of the action
        """

        return self.filter(
            target_object_id = obj.id
        ).order_by('-timestamp')

class FollowManager(models.Manager):
    def stream_for_user(self, user):
        """
        Produces a QuerySet of most recent activities from actors the user follows
        """
        follows = self.filter(user=user)
        action_class = self.model.__class__
        qs = (action_class.objects.stream_for_actor(follow.actor) for follow in follows if follow.actor is not None)
        return reduce(or_, qs, action_class.objects.none()).order_by('-timestamp')
