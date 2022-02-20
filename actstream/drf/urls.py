from rest_framework import routers

from actstream.drf.views import FollowViewSet, ActionViewSet, registered_viewsets

router = routers.DefaultRouter()
router.register(r'actions', ActionViewSet)
router.register(r'follows', FollowViewSet)

for model_class, viewset in registered_viewsets.items():
    router.register(f'{model_class.__name__.lower()}s', viewset)
