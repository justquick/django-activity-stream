Following/Unfollowing Actors
=============================

Creating or deleting the link between a ``User`` and any particular ``Actor`` is as easy as calling a function

.. code-block:: python

    from actstream import follow, unfollow

    follow(request.user, group)
    #OR
    unfollow(request.user, group)

You can also just make a ``GET`` request to the ``actstream_follow`` view while authenticated

.. code-block:: curl

    GET /activity/follow/<content_type_id>/<object_id>/ # Follow
    GET /activity/unfollow/<content_type_id>/<object_id>/?next=/blog/ # Unfollow and redirect

Then the current logged in user will follow the actor defined by ``content_type_id`` & ``object_id``. Optional ``next`` parameter is URL to redirect to.

There is also a function ``actstream.unfollow`` which removes the link and takes the same arguments as ``actstream.follow``
