from django.conf.urls import url

from actstream import feeds, views


urlpatterns = [
    # User feeds
    url(r'^feed/$', feeds.UserActivityFeed(), name='actstream_feed'),
    url(r'^feed/atom/$', feeds.AtomUserActivityFeed(),
        name='actstream_feed_atom'),
    url(r'^feed/json/$', feeds.UserJSONActivityFeed.as_view(),
        name='actstream_feed_json'),

    # Model feeds
    url(
        r'^feed/(?P<content_type_id>[^/]+)/$',
        feeds.ModelActivityFeed(),
        name='actstream_model_feed'
    ),
    url(
        r'^feed/(?P<content_type_id>[^/]+)/atom/$',
        feeds.AtomModelActivityFeed(),
        name='actstream_model_feed_atom'
    ),
    url(
        r'^feed/(?P<content_type_id>[^/]+)/json/$',
        feeds.ModelJSONActivityFeed.as_view(),
        name='actstream_model_feed_json'
    ),

    # Object feeds
    url(
        r'^feed/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/$',
        feeds.ObjectActivityFeed(),
        name='actstream_object_feed'
    ),
    url(
        r'^feed/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/atom/$',
        feeds.AtomObjectActivityFeed(),
        name='actstream_object_feed_atom'
    ),
    url(
        r'^feed/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/json/$',
        feeds.ObjectJSONActivityFeed.as_view(),
        name='actstream_object_feed_json'
    ),

    # Follow/Unfollow API
    url(
        r'^follow/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/(?:(?P<flag>[^/]+)/)?$',
        views.follow_unfollow,
        name='actstream_follow'
    ),
    url(
        r'^follow_all/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/(?:(?P<flag>[^/]+)/)?$',
        views.follow_unfollow,
        {'actor_only': False},
        name='actstream_follow_all'
    ),
    url(
        r'^unfollow_all/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/(?:(?P<flag>[^/]+)/)?$',
        views.follow_unfollow,
        {'actor_only': False, 'do_follow': False},
        name='actstream_unfollow_all'
    ),
    url(
        r'^unfollow/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/(?:(?P<flag>[^/]+)/)?$',
        views.follow_unfollow,
        {'do_follow': False},
        name='actstream_unfollow'
    ),

    # Follower and Actor lists
    url(
        r'^followers/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/(?:(?P<flag>[^/]+)/)?$',
        views.followers,
        name='actstream_followers'
    ),
    url(
        r'^following/(?P<user_id>[^/]+)/(?:(?P<flag>[^/]+)/)?$',
        views.following,
        name='actstream_following'
    ),
    url(
        r'^actors/(?P<content_type_id>[^/]+)/(?P<object_id>[^/]+)/$',
        views.actor,
        name='actstream_actor'
    ),
    url(
        r'^actors/(?P<content_type_id>[^/]+)/$',
        views.model,
        name='actstream_model'
    ),

    url(
        r'^detail/(?P<action_id>[^/]+)/$',
        views.detail,
        name='actstream_detail'
    ),
    url(
        r'^(?P<username>[^/]+)/$',
        views.user,
        name='actstream_user'
    ),
    url(
        r'^$',
        views.stream,
        name='actstream'
    ),
]
