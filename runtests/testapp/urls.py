from django.urls import re_path, path
from django.conf import settings

from actstream import feeds


urlpatterns = [
    re_path(r'custom/(?P<verb>[-\w\s]+)/',
            feeds.CustomJSONActivityFeed.as_view(name='testbar'),
            name='testapp_custom_feed'),
]

if 'drf_spectacular' in settings.INSTALLED_APPS:
    from .views import SpectacularRapiDocView
    urlpatterns += [path('rapidoc/', SpectacularRapiDocView.as_view())]
