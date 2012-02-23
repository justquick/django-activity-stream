Following/Unfollowing Actors
=============================

Creating or deleting the link between a ``User`` and any particular ``Actor`` is as easy as calling a function

.. code-block:: python

    from actstream import follow, unfollow

    follow(request.user, group)
    #OR
    unfollow(request.user, group)

You can also just make a request to the ``actstream_follow`` view while authenticated.
The request can use either ``GET`` or ``POST``.

.. code-block:: bash

    curl -X GET http://localhost:8000/activity/follow/<content_type_id>/<object_id>/ # Follow
    curl -X GET http://localhost:8000/activity/unfollow/<content_type_id>/<object_id>/?next=/blog/ # Unfollow and redirect

Then the current logged in user will follow the actor defined by ``content_type_id`` & ``object_id``. Optional ``next`` parameter is URL to redirect to.

There is also a function ``actstream.unfollow`` which removes the link and takes the same arguments as ``actstream.follow``
