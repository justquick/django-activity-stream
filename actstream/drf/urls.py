from django.utils.text import slugify

from rest_framework import routers

from actstream.drf.views import FollowViewSet, ActionViewSet, registered_viewsets


# Default names for actstream models
router = routers.DefaultRouter()
router.register(r'actions', ActionViewSet)
router.register(r'follows', FollowViewSet)

# register a router for each model_class in the registry
for model_class, viewset in registered_viewsets.items():
    name = str(slugify(model_class._meta.verbose_name_plural))
    router.register(name, viewset)

urlpatterns = router.urls
