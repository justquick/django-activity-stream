from django.conf.urls.defaults import *


urlpatterns = patterns('actstream.views',
    url(r'^follow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'follow', name='actstream_follow'),
    url(r'^(?P<username>[-\w]+)/$', 'user', name='actstream_user'),
    url(r'^$', 'stream', name='actstream'),
)
