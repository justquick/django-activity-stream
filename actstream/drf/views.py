from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response


from actstream.drf.serializers import FollowSerializer, ActionSerializer, registered_serializers, registry_factory
from actstream.models import Action, Follow, actor_stream
from actstream.registry import label
from actstream.settings import DRF_SETTINGS, import_obj


class DefaultModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_permissions(self):
        return [import_obj(permission)() for permission in DRF_SETTINGS['PERMISSIONS']]


class ActionViewSet(DefaultModelViewSet):
    queryset = Action.objects.public().prefetch_related()
    serializer_class = ActionSerializer

    @action(detail=False, methods=['POST'])
    def send(self, request):
        pass

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


class FollowViewSet(DefaultModelViewSet):
    queryset = Follow.objects.prefetch_related()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ordering = ['started']

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
