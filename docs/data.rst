.. _custom-data:

Custom Action Data
==================

In a New Project
----------------

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

Adding to Existing Project
--------------------------

If you start out your project with ``USE_JSONFIELD=False``, dont worry you can add it afterwards.

Make sure you have the latest JSONField implementation

.. code-block::

    pip install django-activity-stream[jsonfield]

Make sure ``USE_JSONFIELD`` is non-existent or set to False then do the initial migration

.. code-block:: bash

    python manage.py migrate actstream 0001

Update the setting

.. code-block:: python

    ACTSTREAM_SETTINGS = {
        "USE_JSONFIELD": True,
    }

Then migrate the whole app

.. code-block:: bash

    python manage.py migrate actstream
