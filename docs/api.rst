API
===

Actions
-------

.. automodule:: actstream.actions
    :members: follow, unfollow, is_following, action_handler

Action Manager
--------------

.. autoclass:: actstream.managers.ActionManager
    :members: public, actor, target, model_actions, action_object, any, user

Follow Manager
--------------

.. autoclass:: actstream.managers.FollowManager
    :members: followers, following, is_following, for_object

Views
-----

.. automodule:: actstream.views
    :members: respond, follow_unfollow, stream, followers, following, user, detail, actor, model


ReST API
--------

.. autoclass:: actstream.drf.views.ActionViewSet
    :members:

.. autoclass:: actstream.drf.views.FollowViewSet
    :members:

.. autoclass:: actstream.drf.serializers.ActionSerializer
    :members:

Feeds
-----

.. autoclass:: actstream.feeds.AbstractActivityStream
    :members:

Atom
^^^^

Compatible with `Atom Activity Streams 1.0 <http://activitystrea.ms/specs/atom/1.0/>`_ spec

.. autoclass:: actstream.feeds.AtomUserActivityFeed
.. autoclass:: actstream.feeds.AtomModelActivityFeed
.. autoclass:: actstream.feeds.AtomObjectActivityFeed

JSON
^^^^

Compatible with `JSON Activity Streams 1.0 <http://activitystrea.ms/specs/json/1.0/>`_ spec

.. autoclass:: actstream.feeds.AtomUserActivityFeed
.. autoclass:: actstream.feeds.AtomModelActivityFeed
.. autoclass:: actstream.feeds.AtomObjectActivityFeed


Decorators
----------

.. automodule:: actstream.decorators
    :members: stream

Templatetags
------------

Start off your templates by adding::

    {% load activity_tags %}

.. automodule:: actstream.templatetags.activity_tags
    :members: activity_stream, is_following, display_action, follow_url, follow_all_url, actor_url
