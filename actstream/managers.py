from collections import defaultdict
from operator import or_

from django.db.models import Q
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

from actstream.exceptions import check_actionable_model
from actstream.gfk import GFKManager, EmptyGFKQuerySet
from actstream.exceptions import BadQuerySet
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
        return self.public(Q(target_content_type = ctype)|\
            Q(action_object_content_type = ctype)|\
            Q(actor_content_type = ctype))

    @stream
    def user(self, object, **kwargs):
        """
        Stream of most recent actions by actors that the passed User object is following
        """
        from actstream.models import Follow
        q = Q()
        qs = self.filter(public=True)
        actors_by_content_type = defaultdict(lambda: [])

        follow_gfks = Follow.objects.filter(user=object).values_list(
            'content_type_id', 'object_id')
        for content_type_id, object_id in follow_gfks.iterator():
            actors_by_content_type[content_type_id].append(object_id)

        for content_type_id, object_ids in actors_by_content_type.iteritems():
            q = q | Q(
                actor_content_type = content_type_id,
                actor_object_id__in = object_ids,
            )
        qs = qs.filter(q)
        return qs

