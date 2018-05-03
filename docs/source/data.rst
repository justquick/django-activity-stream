.. _custom-data:

Adding Custom Data to your Actions
==================================

django-activity-stream supports adding custom data to any Actions you generate.
This uses a ``data`` JSONField on every Action where you can insert and delete
values at will. This behavior is disabled by default but just set
``ACTSTREAM_SETTINGS['USE_JSONFIELD'] = True`` in your settings.py to enable
it.

If you're using a postgresql database and you'd like to use the JSONField
included with Django, set ``USE_NATIVE_JSONFIELD = True`` in your settings file.
See
`django-jsonfield-compat <https://github.com/kbussell/django-jsonfield-compat#installation>`_
for more information.


.. note::

    This feature requires that you have `django-jsonfield <https://bitbucket.org/schinckel/django-jsonfield/>`_ installed.

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

Data in custom Action models
----------------------------

If you'd like to store custom data as separate model fields, you can swap the
Action model for one of your own:

.. code-block:: django

    from actstream.models import AbstractAction
    from django.db import models
    from django.utils.translation import ugettext_lazy as _

    class CustomAction(AbstractAction):
        quest = models.CharField(_('quest'), max_length=255, blank=True, null=True)


And then set ``ACTSTREAM_ACTION_MODEL = 'myapp.CustomAction'`` in your
project's settings. Like previously, send extra data as keyword arguments to
the ``action`` signal and django-activity-stream will figure out the rest.
