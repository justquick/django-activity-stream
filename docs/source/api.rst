API
===

Action Manager
--------------

.. autoclass:: actstream.managers.ActionManager
    :members: public, actor, target, model_actions, action_object, user

Views
------

.. automodule:: actstream.views
    :members: respond, follow_unfollow, stream, followers, user, detail, actor, model

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