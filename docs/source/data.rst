.. _custom-data:

Adding Custom Data to your Actions
==================================

As of v0.4.4, django-activity-stream now supports adding custom data to any Actions you generate.
This uses a ``data`` JSONField on every Action where you can insert and delete values at will.
This behavior is disabled by default but just set ``ACTSTREAM_SETTINGS['USE_JSONFIELD'] = True`` in your
settings.py to enable it. If you're running Django >= 1.9 and you'd like to use the JSONField included
with Django, set ``USE_NATIVE_JSONFIELD = True`` in your settings file.

.. note::

  Multiple implementations of the JSONField are supported, depending on which packages are installed:

  - The default and preferred implementation is used by installing **both** `django-jsonfield <https://bitbucket.org/schinckel/django-jsonfield/>`_ and `django-jsonfield-compat <https://github.com/kbussell/django-jsonfield-compat>`_. This is also allowing to use Django's native JSONField as described above.
  - Alternatively you can install **only** `django-mysql <https://github.com/adamchainz/django-mysql>`_ (*requires MySQL 5.7+*) to use its JSONField. Make sure the packages above are **not installed**, as they would be preferred. This can be useful when you are using it already and want to use the same field for actstream.

You can send the custom data as extra keyword arguments to the ``action`` signal.

.. code-block:: python

    action.send(galahad, verb='answered', target=bridgekeeper,
        favorite_color='Blue. No, yel... AAAAAAA')


Now you can retrieve the data dictionary once you grab the action and manipulate it to your liking at anytime.

.. code-block:: python

    >>> action = Action.objects.get(verb='answered', actor=galahad, target=bridgekeeper)
    >>> action.data['favorite_color']
    ... 'Blue. No, yel... AAAAAAA'
    >>> action.data['quest'] = 'To seek the Holy Grail'
    >>> action.save()
    >>> action.data
    ... {'favorite_color': 'Blue. No, Green - AAAAAAA', 'quest': 'To seek the Holy Grail'}

Even in a template

.. code-block:: django

    You are {{ action.actor }} your quest is {{ action.data.quest }} and your favorite color is {{ action.data.favorite_color }}
