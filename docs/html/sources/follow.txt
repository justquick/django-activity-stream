Following/Unfollowing Objects
=============================

Creating or deleting the link between a ``User`` and any particular object is as easy as calling a function:

.. code-block:: python

    from actstream import follow, unfollow

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

There is also a function ``actstream.unfollow`` which removes the link and takes the same arguments as ``actstream.follow``
