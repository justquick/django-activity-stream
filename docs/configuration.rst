Configuration
=============


Model Registration
------------------

In order to have your models be either an actor, target, or action object they must first be registered with actstream.
In v0.5 and above, actstream has a registry of all actionable model classes.
When you register them, actstream sets up certain GenericRelations that are required for generating activity streams.

For Django versions 1.7 or later, you should use `AppConfig <https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications>`_.

.. code-block:: python

    # myapp/apps.py
    from django.apps import AppConfig

    class MyAppConfig(AppConfig):
        name = 'myapp'

        def ready(self):
            from actstream import registry
            registry.register(self.get_model('MyModel'))

    # myapp/__init__.py
    default_app_config = 'myapp.apps.MyAppConfig'


Settings
--------

Update these settings in your project's ``settings.py``.
As of v0.4.4, all settings are contained inside the ``ACTSTREAM_SETTINGS`` dictionary.
Here is an example of what you can set in your ``settings.py``

.. code-block:: python

    ACTSTREAM_SETTINGS = {
        'MANAGER': 'myapp.managers.MyActionManager',
        'FETCH_RELATIONS': True,
        'USE_PREFETCH': True,
        'USE_JSONFIELD': True,
        'GFK_FETCH_DEPTH': 1,
        'DRF': {'ENABLE': True}
    }

.. note::

    Please decide early on whether you want to ``USE_JSONFIELD`` or not, as the ``Action.data`` field will be removed during initial migrations when this option is set to ``False`` (the default).

.. note::

    In v0.5 and above, since only Django>=1.4 is supported all generic lookups fall back to `QuerySet.prefetch_related <https://docs.djangoproject.com/en/dev/ref/models/querysets/#django.db.models.query.QuerySet.prefetch_related>`_
    so the ``USE_PREFETCH`` and ``GFK_FETCH_DEPTH`` settings have been deprecated.


Supported settings are defined below.

.. _manager:

MANAGER
*******

The action manager is the `Django manager <https://docs.djangoproject.com/en/dev/topics/db/managers/>`_ interface used for querying activity data from the database.

The Python import path of the manager to use for ``Action.objects``.
Add your own manager here to create custom streams.
There can only be one manager class per Django project.

For more info, see :ref:`custom-streams`

Defaults to :class:`actstream.managers.ActionManager`

FETCH_RELATIONS
***************

Set this to ``False`` to disable ``select_related`` and ``prefetch_related`` when querying for any streams.
When ``True``, related generic foreign keys will be prefetched for stream generation (preferable).

Defaults to ``True``

USE_PREFETCH
************

.. deprecated:: 0.5

    This setting is no longer used (see note above).

Set this to ``True`` to forcefully enable ``prefetch_related`` (Django>=1.4 only).
On earlier versions, the generic foreign key prefetch fallback contained within ``actstream.gfk`` will be enabled.

Defaults to whatever version you have.

USE_JSONFIELD
*************

Set this setting to ``True`` to enable the ``Action.data`` JSONField for all actions.
Lets you add custom data to any of your actions, see :ref:`custom-data`

Defaults to ``False``


DRF
***

Enable this group of settings to use the django-rest-framework integration. 
Fore more information about the available settings see :ref:`drf`


GFK_FETCH_DEPTH
***************

.. deprecated:: 0.5

    This setting is no longer used (see note above).

Number of levels of relations that ``select_related`` will perform.
Only matters if you are not running ``prefetch_related`` (Django<=1.3).

Defaults to ``0``
