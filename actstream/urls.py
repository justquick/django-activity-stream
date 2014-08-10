try:
    from django.conf.urls import url, patterns
except ImportError:
    from django.conf.urls.defaults import url, patterns

from actstream import feeds


urlpatterns = patterns('actstream.views',
    # User feeds
    url(r'^feed/$', feeds.UserActivityFeed(), name='actstream_feed'),
    url(r'^feed/atom/$', feeds.AtomUserActivityFeed(),
        name='actstream_feed_atom'),
    url(r'^feed/json/$', feeds.UserJSONActivityFeed.as_view(),
        name='actstream_feed_json'),

    # Object feeds
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        feeds.ObjectActivityFeed(), name='actstream_object_feed'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/atom/$',
        feeds.AtomObjectActivityFeed(), name='actstream_object_feed_atom'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/json/$',
        feeds.ObjectJSONActivityFeed.as_view(), name='actstream_object_feed_json'),

    # Model feeds
    url(r'^feed/(?P<content_type_id>\d+)/$',
        feeds.ModelActivityFeed(), name='actstream_model_feed'),
    url(r'^feed/(?P<content_type_id>\d+)/atom/$',
        feeds.AtomModelActivityFeed(), name='actstream_model_feed_atom'),
    url(r'^feed/(?P<content_type_id>\d+)/json/$',
        feeds.ModelJSONActivityFeed.as_view(), name='actstream_model_feed_json'),

    # Follow/Unfollow API
    url(r'^follow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'follow_unfollow', name='actstream_follow'),
    url(r'^follow_all/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'follow_unfollow', {'actor_only': False}, name='actstream_follow_all'),
    url(r'^unfollow/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'follow_unfollow', {'do_follow': False}, name='actstream_unfollow'),

    # Follower and Actor lists
    url(r'^followers/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'followers', name='actstream_followers'),
    url(r'^actors/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$',
        'actor', name='actstream_actor'),
    url(r'^actors/(?P<content_type_id>\d+)/$',
        'model', name='actstream_model'),

    url(r'^detail/(?P<action_id>\d+)/$', 'detail', name='actstream_detail'),
    url(r'^(?P<username>.+)/$', 'user', name='actstream_user'),
    url(r'^$', 'stream', name='actstream'),
)
