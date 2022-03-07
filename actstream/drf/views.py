from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response


from actstream.drf.serializers import FollowSerializer, ActionSerializer, registered_serializers, registry_factory
from actstream import models  # import Action, Follow, actor_stream, model_stream, any_stream
from actstream.registry import label
from actstream.settings import DRF_SETTINGS, import_obj
from actstream.signals import action as action_signal
from actstream.actions import follow as follow_action


class DefaultModelViewSet(viewsets.ReadOnlyModelViewSet):

    def get_permissions(self):
        if isinstance(DRF_SETTINGS['PERMISSIONS'], (tuple, list)):
            return [import_obj(permission)() for permission in DRF_SETTINGS['PERMISSIONS']]
        if isinstance(DRF_SETTINGS['PERMISSIONS'], dict):
            lookup = {key.lower(): value for key, value in DRF_SETTINGS['PERMISSIONS'].items()}
            model_label = label(self.get_serializer().Meta.model).lower()
            if model_label in lookup:
                permissions = lookup[model_label]
                if isinstance(permissions, str):
                    permissions = [import_obj(permissions)()]
                else:
                    permissions = [import_obj(permission)() for permission in permissions]
                return permissions
        return []


class ActionViewSet(DefaultModelViewSet):
    queryset = models.Action.objects.public().order_by('-timestamp', '-id').prefetch_related()
    serializer_class = ActionSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated], methods=['POST'])
    def send(self, request):
        """
        Sends the action signal on POST
        Must have a verb and optional target/action_object with content_type_id/object_id pairs
        Actor is set as current logged in user
        """
        data = request.data.dict()
        if 'verb' not in data:
            return Response(status=400)

        for name in ('target', 'action_object'):
            if f'{name}_content_type_id' in data and f'{name}_object_id' in data:
                ctype = get_object_or_404(ContentType, id=data.pop(f'{name}_content_type_id'))
                data[name] = ctype.get_object_for_this_type(pk=data.pop(f'{name}_object_id'))

        action_signal.send(sender=request.user, **data)
        return Response(status=201)

    def get_stream(self, stream):
        """
        Helper for paginating streams and serializing responses
        """
        page = self.paginate_queryset(stream)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(stream, many=True)
        return Response(serializer.data)

    def get_detail_stream(self, stream, content_type_id, object_id):
        """
        Helper for returning a stream that takes a content type/object id to lookup an instance
        """
        content_type = get_object_or_404(ContentType, id=content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
        return self.get_stream(stream(obj))

    @action(detail=False, url_path='streams/my-actions', permission_classes=[permissions.IsAuthenticated], name='My Actions')
    def my_actions(self, request):
        """
        Returns all actions where the current user is the actor
        See models.actor_stream
        """
        return self.get_stream(models.actor_stream(request.user))

    @action(detail=False, url_path='streams/following',  permission_classes=[permissions.IsAuthenticated], name='Actions by followed users')
    def following(self, request):
        """
        Returns all actions for users that the current user follows
        See models.user_stream
        """
        kwargs = request.query_params.dict()
        return self.get_stream(models.user_stream(request.user, **kwargs))

    @action(detail=False, url_path='streams/model/(?P<content_type_id>[^/.]+)', name='Model activity stream')
    def model_stream(self, request, content_type_id):
        """
        Returns all actions for a given content type.
        See models.model_stream
        """
        content_type = get_object_or_404(ContentType, id=content_type_id)
        return self.get_stream(models.model_stream(content_type.model_class()))

    @action(detail=False, url_path='streams/actor/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)', name='Actor activity stream')
    def actor_stream(self, request, content_type_id, object_id):
        """
        Returns all actions for a given object where the object is the actor
        See models.actor_stream
        """
        return self.get_detail_stream(models.actor_stream, content_type_id, object_id)

    @action(detail=False, url_path='streams/target/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)', name='Target activity stream')
    def target_stream(self, request, content_type_id, object_id):
        """
        Returns all actions for a given object where the object is the target
        See models.target_stream
        """
        return self.get_detail_stream(models.target_stream, content_type_id, object_id)

    @action(detail=False, url_path='streams/action_object/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)', name='Action object activity stream')
    def action_object_stream(self, request, content_type_id, object_id):
        """
        Returns all actions for a given object where the object is the action object
        See models.action_object_stream
        """
        return self.get_detail_stream(models.action_object_stream, content_type_id, object_id)

    @action(detail=False, url_path='streams/any/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)', name='Any activity stream')
    def any_stream(self, request, content_type_id, object_id):
        """
        Returns all actions for a given object where the object is any actor/target/action_object
        See models.any_stream
        """
        return self.get_detail_stream(models.any_stream, content_type_id, object_id)


class FollowViewSet(DefaultModelViewSet):
    queryset = models.Follow.objects.order_by('-started', '-id').prefetch_related()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, permission_classes=[permissions.IsAuthenticated], methods=['POST'])
    def follow(self, request):
        """
        Creates the follow relationship.
        The current user is set as user and the target is passed with content_type_id/object_id pair
        """
        data = request.data.dict()
        if 'content_type_id' not in data:
            return Response(status=400)
        ctype = get_object_or_404(ContentType, id=data.pop('content_type_id'))
        obj = ctype.get_object_for_this_type(pk=data.pop('object_id'))
        follow_action(request.user, obj, **data)
        return Response(status=201)


def viewset_factory(model_class, queryset=None):
    """
    Returns a subclass of `ModelViewSet` for each model class in the registry
    """
    if queryset is None:
        queryset = model_class.objects.prefetch_related()
    serializer_class = registered_serializers[model_class]
    model_label = label(model_class)
    if model_label in DRF_SETTINGS['VIEWSETS']:
        return import_obj(DRF_SETTINGS['VIEWSETS'][model_label])
    return type(f'{model_class.__name__}ViewSet', (DefaultModelViewSet,), {
        'queryset': queryset,
        'serializer_class': serializer_class,
    })


registered_viewsets = registry_factory(viewset_factory)
