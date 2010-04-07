from django.conf.urls.defaults import *
from django.conf import settings
from actstream.feeds import *

urlpatterns = patterns('actstream.views',
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/atom/$', AtomObjectActivityFeed(), name='actstream_object_feed_atom'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', ObjectActivityFeed(), name='actstream_object_feed'),
    url(r'^feed/(?P<content_type_id>\d+)/atom/$', AtomModelActivityFeed(), name='actstream_model_feed_atom'),    
    url(r'^feed/(?P<content_type_id>\d+)/$', ModelActivityFeed(), name='actstream_model_feed'),
    url(r'^feed/$', UserActivityFeed(), name='actstream_feed'),
    url(r'^feed/atom/$', AtomUserActivityFeed(), name='actstream_feed_atom'),    
    
    url(r'^follow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'follow', name='actstream_follow'),
    url(r'^followers/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'followers', name='actstream_followers'),
    url(r'^actors/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'actor', name='actstream_actor'),
    url(r'^actors/(?P<content_type_id>\d+)/$',
        'model', name='actstream_model'),    
    
    url(r'^detail/(?P<action_id>\d+)/$', 'detail', name='actstream_detail'),
    url(r'^(?P<username>[-\w]+)/$', 'user', name='actstream_user'),
    url(r'^$', 'stream', name='actstream'),
)
