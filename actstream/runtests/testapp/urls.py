import django
try:
    from django.conf.urls import url, patterns
except ImportError:
    from django.conf.urls.defaults import url, patterns

from actstream import feeds

urlpatterns = [
    url(r'^custom/(?P<verb>[-\w\s]+)/$',
        feeds.CustomJSONActivityFeed.as_view(name='testbar'),
        name='testapp_custom_feed'),
]

if django.VERSION[:2] < (1, 9):
    urlpatterns = patterns('', *urlpatterns)
