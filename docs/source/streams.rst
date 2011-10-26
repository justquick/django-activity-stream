Action Streams
===============

Listings of actions are available for several points of view.
All streams return a ``QuerySet`` of ``Action`` items sorted by ``-timestamp``.


Using Builtin Streams
**********************

There are several builtin streams which cover the basics, but you are never limited to them.

User
-----

User streams are the most important, like your News Feed on `github <https://github.com/>`_. Basically you follow anyone (or anything) on your site and their actions show up here.
These streams take one argument which is a ``User`` instance which is the one doing the following (usually ``request.user``)

.. code-block:: python

    from actstream.models import user_stream

    user_stream(request.user)

Generates a stream of ``Actions`` from objects that ``request.user`` follows

Actor
------

Actor streams show you what a particular actor object has done. Helpful for viewing "My Activities".

.. code-block:: python

    from actstream.models import actor_stream

    actor_stream(request.user)

Generates a stream of ``Actions`` where the ``request.user`` was the ``actor``


Action Object
--------------

Action object streams show you what actions a particular instance was used as the ``action_objct``

.. code-block:: python

    from actstream.models import action_object_stream

    action_object_stream(comment)

Generates a stream of ``Actions`` where the ``comment`` was generated as the ``action_object``

Model
------

Model streams offer a much broader scope showing ALL ``Actions`` from any particular model.
Argument may be a class or instance of the model.

.. code-block:: python

    from actstream.models import model_stream

    model_stream(request.user)

Generates a stream of ``Actions`` from all ``User`` instances.


.. _custom-streams:

Writing Custom Streams
***********************

You can override and extend the Action manager ``Action.objects`` to add your own streams.
The setting ``ACTSTREAM_MANAGER`` tells the app which manager to import and use.
The builtin streams are defined in ``actstream/managers.py`` and you should check out how they are written.
Streams must use the ``@stream`` decorator.
They must take at least one argument which is a model instance to be used for reference when creating streams.
Streams may return:

 * ``dict`` - ``Action`` queryset parameters to be AND'd together
 * ``tuple`` of ``dicts`` - tuple of ``Action`` queryset parameter dicts to be OR'd together
 * ``QuerySet`` - raw queryset of ``Action`` objects

When returning a queryset, you do NOT need to call ``fetch_generic_relations()`` or ``select_related(..)``.

Example
--------

To start writing your custom stream module, create a file in your app called ``managers.py``

.. code-block:: python

    # myapp/managers.py
    from datetime import datetime

    from django.contrib.contenttypes.models import ContentType

    from actstream.managers import ActionManager, stream

    class MyActionManager(ActionManager):

        @stream
        def mystream(self, object, verb='posted', time=None):
            if time is None:
                time = datetime.now()
            return object.actor_actions.filter(verb = verb, timestamp__lte = time)

This defines a manager with one stream which filters actions by verb and timestamp.

Now that stream is available directly on the ``Action`` manager through ``Action.objects.mystream``
or from the ``GenericRelation`` on any actionable model instance.

.. code-block:: python

    from django.contrib.auth.models import User
    from actstream.models import Action

    user = User.objects.all()[0]

    Action.objects.mystream(user, 'commented')
    #OR
    user_instance.actor_actions.mystream('commented')
