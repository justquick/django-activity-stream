from rest_framework import viewsets
from rest_framework import permissions

from actstream.drf.serializers import FollowSerializer, ActionSerializer, registered_serializers, registry_factory
from actstream.models import Action, Follow
from actstream.settings import DRF_SETTINGS

DEFAULT_VIEWSET = viewsets.ReadOnlyModelViewSet


class ActionViewSet(DEFAULT_VIEWSET):
    queryset = Action.objects.public().prefetch_related()
    serializer_class = ActionSerializer
    permission_classes = [permissions.IsAuthenticated]


class FollowViewSet(DEFAULT_VIEWSET):
    queryset = Follow.objects.prefetch_related()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]


def viewset_factory(model_class, queryset=None):
    if queryset is None:
        queryset = model_class.objects.prefetch_related()
    serializer_class = registered_serializers[model_class]
    viewset_class = DRF_SETTINGS['VIEWSETS'].get(model_class, DEFAULT_VIEWSET)
    return type(f'{model_class.__name__}ViewSet', (viewset_class,), {
        'queryset': queryset,
        'serializer_class': serializer_class,
        'permission_classes': [permissions.IsAuthenticated]
    })


registered_viewsets = registry_factory(viewset_factory)
