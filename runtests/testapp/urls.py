from django.urls import re_path, include, path

from actstream import feeds
from actstream.drf.urls import router

urlpatterns = [
    path('api/', include(router.urls)),
    re_path(r'custom/(?P<verb>[-\w\s]+)/',
            feeds.CustomJSONActivityFeed.as_view(name='testbar'),
            name='testapp_custom_feed'),
]
