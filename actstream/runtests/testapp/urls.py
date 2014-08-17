try:
    from django.conf.urls import url, patterns
except ImportError:
    from django.conf.urls.defaults import url, patterns

from actstream import feeds

urlpatterns = patterns('',
    url(r'^custom/(?P<verb>[-\w\s]+)/$',
        feeds.CustomJSONActivityFeed.as_view(name='testbar'),
        name='testapp_custom_feed'),
)
