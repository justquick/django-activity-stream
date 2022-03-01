from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response


from actstream.drf.serializers import FollowSerializer, ActionSerializer, registered_serializers, registry_factory
from actstream.models import Action, Follow, actor_stream, model_stream, any_stream
from actstream.registry import label
from actstream.settings import DRF_SETTINGS, import_obj
from actstream.signals import action as action_signal


class DefaultModelViewSet(viewsets.ReadOnlyModelViewSet):
    _permission_cache = {}

    def get_permissions(self):
        if isinstance(DRF_SETTINGS['PERMISSIONS'], (tuple, list)):
            return [import_obj(permission)() for permission in DRF_SETTINGS['PERMISSIONS']]
        if isinstance(DRF_SETTINGS['PERMISSIONS'], dict):
            lookup = {key.lower(): value for key, value in DRF_SETTINGS['PERMISSIONS'].items()}
            model_label = label(self.get_serializer().Meta.model).lower()
            if model_label in self._permission_cache:
                return self._permission_cache[model_label]
            if model_label in lookup:
                permissions = lookup[model_label]
                if isinstance(permissions, str):
                    permissions = [import_obj(permissions)()]
                else:
                    permissions = [import_obj(permission)() for permission in permissions]
                self._permission_cache[model_label] = permissions
                return permissions
        return []


class ActionViewSet(DefaultModelViewSet):
    queryset = Action.objects.public().prefetch_related()
    serializer_class = ActionSerializer
    ordering_fields = ordering = ['-timestamp']

    @action(detail=False, permission_classes=[permissions.IsAuthenticated], methods=['POST'])
    def send(self, request):
        data = request.data.dict()

        for name in ('target', 'action_object'):
            if f'{name}_content_type_id' in data and f'{name}_object_id' in data:
                ctype = get_object_or_404(ContentType, id=data.pop(f'{name}_content_type_id'))
                data[name] = ctype.get_object_for_this_type(pk=data.pop(f'{name}_object_id'))

        action_signal.send(sender=request.user, **data)
        return Response(status=201)

    def get_stream(self, stream):
        page = self.paginate_queryset(stream)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(stream, many=True)
        return Response(serializer.data)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated], name='My Actions')
    def me(self, request):
        return self.get_stream(actor_stream(request.user))

    @action(detail=False, url_path='model/(?P<content_type_id>[^/.]+)', name='Model activity stream')
    def model(self, request, content_type_id):
        content_type = get_object_or_404(ContentType, id=content_type_id)
        return self.get_stream(model_stream(content_type.model_class()))

    @action(detail=False, url_path='object/(?P<content_type_id>[^/.]+)/(?P<object_id>[^/.]+)', name='Object activity stream')
    def object(self, request, content_type_id, object_id):
        content_type = get_object_or_404(ContentType, id=content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
        return self.get_stream(any_stream(obj))


class FollowViewSet(DefaultModelViewSet):
    queryset = Follow.objects.prefetch_related()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ordering = ['-started']

    @action(detail=False, methods=['POST'])
    def follow(self, request):
        pass


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
