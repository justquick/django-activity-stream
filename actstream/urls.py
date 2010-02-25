from django.conf.urls.defaults import *
from feeds import UserActivityFeed, ActorActivityFeed

urlpatterns = patterns('actstream.views',
    url(r'^feed/$', ActorActivityFeed()),    
    url(r'^feed/(?P<username>[-\w]+)/$', UserActivityFeed()),
    url(r'^follow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'follow', name='actstream_follow'),
    url(r'^detail/(?P<activity_id>\d+)/$', 'detail', name='actstream_detail'),
    url(r'^(?P<username>[-\w]+)/$', 'user', name='actstream_user'),
    url(r'^$', 'stream', name='actstream'),
)
