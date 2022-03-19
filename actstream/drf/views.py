import json

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import APIException, NotFound

from actstream.drf import serializers
from actstream import models
from actstream.registry import label
from actstream.settings import DRF_SETTINGS, import_obj
from actstream.signals import action as action_signal
from actstream.actions import follow as follow_action


def get_or_not_found(klass, detail=None, **kwargs):
    try:
        return klass.objects.get(**kwargs)
    except klass.DoesNotExist:
        raise NotFound(detail, 404)


class ModelNotRegistered(APIException):
    status_code = 400
    default_detail = 'Model requested was not registered. Use actstream.registry.register to add it'
    default_code = 'model_not_registered'


class DefaultModelViewSet(viewsets.ReadOnlyModelViewSet):

    def get_permissions(self):
        if isinstance(DRF_SETTINGS['PERMISSIONS'], (tuple, list)):
            return [import_obj(permission)() for permission in DRF_SETTINGS['PERMISSIONS']]
        if isinstance(DRF_SETTINGS['PERMISSIONS'], dict):
            lookup = {key.lower(): value for key, value in DRF_SETTINGS['PERMISSIONS'].items()}
            serializer = self.get_serializer()
            if hasattr(serializer, 'Meta') and hasattr(serializer.Meta, 'model'):
                model_label = label(serializer.Meta.model).lower()
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
    serializer_class = serializers.ActionSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated], methods=['POST'], serializer_class=serializers.SendActionSerializer)
    def send(self, request):
        """
        Sends the action signal on POST
        Must have a verb and optional target/action_object with content_type_id/object_id pairs
        Actor is set as current logged in user
        """
        data = request.data
        if hasattr(data, 'dict'):
            data = data.dict()
        if 'verb' not in data:
            return Response(status=400)

        for name in ('target', 'action_object'):
            if f'{name}_content_type_id' in data and f'{name}_object_id' in data:
                ctype = get_or_not_found(
                    ContentType, f'ContentType for {name} query does not exist', pk=data.pop(f'{name}_content_type_id'))
                data[name] = get_or_not_found(ctype.model_class(), f'Object for {name} query does not exist', pk=data.pop(f'{name}_object_id'))

        # dont let users define timestamp
        data.pop('timestamp', None)

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
    serializer_class = serializers.FollowSerializer
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

    @action(detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path='is_following/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)', name='True if user is following object')
    def is_following(self, request,  content_type_id, object_id):
        """
        Returns a JSON response whether the current user is following the object from content_type_id/object_id pair
        """
        ctype = get_object_or_404(ContentType, id=content_type_id)
        instance = ctype.get_object_for_this_type(pk=object_id)
        following = models.Follow.objects.is_following(request.user, instance)
        data = {'is_following': following}
        return Response(json.dumps(data))

    @action(detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path='following', name='List of instances I follow')
    def following(self, request):
        """
        Returns a JSON response whether the current user is following the object from content_type_id/object_id pair
        """
        qs = models.Follow.objects.following_qs(request.user)
        return Response(serializers.FollowingSerializer(qs, many=True).data)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path='followers', name='List of followers for current user')
    def followers(self, request):
        """
        Returns a JSON response whether the current user is following the object from content_type_id/object_id pair
        """
        user_model = get_user_model()
        if user_model not in serializers.registered_serializers:
            raise ModelNotRegistered(f'Auth user "{user_model.__name__}" not registered with actstream')
        serializer = serializers.registered_serializers[user_model]
        followers = models.Follow.objects.followers(request.user)
        return Response(serializer(followers, many=True).data)


def viewset_factory(model_class, queryset=None):
    """
    Returns a subclass of `ModelViewSet` for each model class in the registry
    """
    if queryset is None:
        queryset = model_class.objects.prefetch_related()
    serializer_class = serializers.registered_serializers[model_class]
    model_label = label(model_class)
    if model_label in DRF_SETTINGS['VIEWSETS']:
        return import_obj(DRF_SETTINGS['VIEWSETS'][model_label])
    return type(f'{model_class.__name__}ViewSet', (DefaultModelViewSet,), {
        'queryset': queryset,
        'serializer_class': serializer_class,
    })


registered_viewsets = serializers.registry_factory(viewset_factory)
