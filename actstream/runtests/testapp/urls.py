try:
    from django.urls import url
except ImportError:
    from django.conf.urls import url

from actstream import feeds

urlpatterns = [
    url(r'^custom/(?P<verb>[-\w\s]+)/$',
        feeds.CustomJSONActivityFeed.as_view(name='testbar'),
        name='testapp_custom_feed'),
]
