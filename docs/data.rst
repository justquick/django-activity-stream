.. _custom-data:

Adding Custom Data to your Actions
==================================

As of v0.4.4, django-activity-stream now supports adding custom data to any Actions you generate.
This uses a ``data`` JSONField on every Action where you can insert and delete values at will.
This behavior is disabled by default but just set ``ACTSTREAM_SETTINGS['USE_JSONFIELD'] = True`` in your
settings.py to enable it.

.. note::

  If you're running Django < 3.1 you must install django-jsonfield-backport or the extra ``jsonfield`` of this package.
  "django_jsonfield_backport" gets dynamically added to the INSTALLED_APPS of your Django application if not yet done manually.

  Please make sure to remove both the django-jsonfield-backport package and the ``django_jsonfield_backport`` INSTALLED_APPS entry (if manually added) after upgrading to Django >= 3.1

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
