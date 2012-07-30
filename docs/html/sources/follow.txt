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
    following(request.user, User) # returns a list of groups who request.user is following
