Configuration
==============


Models
-------

In order to have your models be either an actor, target, or action object they must first be registered with actstream.
In v0.5 and above, actstream has a registry of all actionable model classes.
When you register them, actstream sets up certain GenericRelations that are required for generating activity streams.

.. warning::

    Introducing the registry change makes the ACTSTREAM_SETTINGS['MODELS'] setting obsolte so please use the register functions instead.


You normally call register right after your model is defined (models.py) but you can call it anytime before you need to generate actions or activity streams.

.. code-block:: python

    # myapp/models.py
    from actstream import registry

    class MyModel(models.Model):
        ...

    # Django < 1.7
    registry.register(MyModel)

For Django versions 1.7 or later, you should use `AppConfig <https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications>`_.

.. code-block:: python

    # myapp/apps.py
    from django.apps import AppConfig
    from actstream import registry

    class MyAppConfig(AppConfig):
        name = 'myapp'

        def ready(self):
            registry.register(self.get_models('MyModel'))

    # myapp/__init__.py
    default_app_config = 'myapp.apps.MyAppConfig'


Settings
--------

Update these settings in your project's ``settings.py``.
As of v0.4.4, all settings are contained inside the ``ACTSTREAM_SETTINGS`` dictionary.
Here is an example of what you can set in your ``settings.py``

.. code-block:: python

    ACTSTREAM_SETTINGS = {
        'MANAGER': 'myapp.streams.MyActionManager',
        'FETCH_RELATIONS': True,
        'USE_PREFETCH': True,
        'USE_JSONFIELD': True,
        'GFK_FETCH_DEPTH': 1,
    }


Supported settings are defined below.


MANAGER
********

The Python import path of the manager to use for ``Action.objects``.
Add your own manager here to create custom streams.

For more info, see :ref:`custom-streams`

Defaults to ``actstream.managers.ActionManager``

FETCH_RELATIONS
***************

Set this to ``False`` to disable ``select_related`` and ``prefetch_related`` when querying for any streams.
When ``True``, related generic foreign keys will be prefetched for stream generation (preferrable).

Defaults to ``True``

USE_PREFETCH
*************

Set this to ``True`` to forcefully enable ``prefetch_related`` (Django>=1.4 only).
On earlier versions, the generic foreign key prefetch fallback contained within ``actstream.gfk`` will be enabled.

Defaults to whatever version you have.

USE_JSONFIELD
*************

Set this setting to ``True`` to enable the ``Action.data`` JSONField for all actions.
Lets you add custom data to any of your actions, see :ref:`custom-data`

Defaults to ``False``


GFK_FETCH_DEPTH
***************

Number of levels of relations that ``select_related`` will perform.
Only matters if you are not running ``prefetch_related`` (Django<=1.3).

Defaults to ``0``
