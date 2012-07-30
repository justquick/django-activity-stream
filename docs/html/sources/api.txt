API
===

Action Manager
--------------

.. autoclass:: actstream.managers.ActionManager
    :members: public, actor, target, model_actions, action_object, user

Follow Manager
--------------

.. autoclass:: actstream.managers.FollowManager
    :members: followers, following, is_following, for_object

Views
------

.. automodule:: actstream.views
    :members: respond, follow_unfollow, stream, followers, following, user, detail, actor, model

Actions
--------

.. automodule:: actstream.actions
    :members: follow, unfollow, is_following, action_handler

Decorators
-----------

.. automodule:: actstream.decorators
    :members: stream

Exceptions
-----------

.. automodule:: actstream.exceptions
    :members: ModelNotActionable, BadQuerySet, check_actionable_model

Templatetags
-------------

.. automodule:: actstream.templatetags.activity_tags
    :members: is_following,display_action,follow_url,actor_url
