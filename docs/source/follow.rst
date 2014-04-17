Following/Unfollowing Objects
=============================

Creating or deleting the link between a ``User`` and any particular object is as easy as calling a function:

.. code-block:: python

    from actstream.actions import follow, unfollow

    # Follow the group (where it is an actor).
    follow(request.user, group)

    # Stop following the group.
    unfollow(request.user, group)

By default, ``follow`` only follows the object where it is an actor. To also
include activity stream items where the object is the target or action_object,
set the ``actor_only`` parameter to ``False``:

.. code-block:: python

    # Follow the group wherever it appears in activity.
    follow(request.user, group, actor_only=False)

You can also just make a request to the ``actstream_follow`` view while authenticated.
The request can use either ``GET`` or ``POST``.

.. code-block:: bash

    curl -X GET http://localhost:8000/activity/follow/<content_type_id>/<object_id>/ # Follow
    curl -X GET http://localhost:8000/activity/unfollow/<content_type_id>/<object_id>/?next=/blog/ # Unfollow and redirect

Then the current logged in user will follow the actor defined by ``content_type_id`` & ``object_id``. Optional ``next`` parameter is URL to redirect to.

You may want to track read / unread actions. To enable this, use the
``track_unread`` keyword. To enable this by default for all calls to
``follow``, use the TRACK_UNREAD_DEFAULT setting.

.. code-block:: python

    # Follows with unread actions tracking
    follow(request.user, group, track_unread=True)

The message retrieved through this follower will be rendered with a
``[unread]`` suffix if using the Action.render method or the
Action.bulk_render classmethod (which is preferable if you have a list or
queryset of Action objects that you wish to render). If the standard
__unicode__ method is used, however, unread actions will remain marked as
unread.

If you don't want the actions to be automatically marked as read when rendered,
you can pass a ``auto_read`` keyword argument to ``follow`` and set it to
``False``. To enable this for all calls to ``follow``, use the
AUTO_READ_DEFAULT setting.

.. code-block:: python

    # Follows with unread actions tracking with automatic read marking disabled
    follow(request.user, group, track_unread=True, auto_read=False)

When ``auto_read`` is set to ``False``, you can mark actions as read for the
user using the Action.mark_read method, Action.bulk_mark_read classmethod or
the Follow.mark_read method with ``force=True``.

.. code-block:: python

    # Marks an action or an iterable of Action objects as unread when
    # auto_read = False
    action.mark_read(user, force=True)
    Action.bulk_mark_read(actions, force=True)
    follow.mark_read(actions, force=True)


There is also a function ``actstream.actions.unfollow`` which removes the link and takes the same arguments as ``actstream.actions.follow``

Now to retrive the follower/following relationships you can use the convient accessors

.. code-block:: python

    from actstream.models import following, followers

    followers(request.user) # returns a list of Users who follow request.user
    following(request.user) # returns a list of actors who request.user is following

To limit the actor models for the following relationship, just pass the model classes

.. code-block:: python

    from django.contrib.auth.models import User, Group

    following(request.user, User) # returns a list of users who request.user is following
    following(request.user, Group) # returns a list of groups who request.user is following
