Configuration
=============


Model Registration
------------------

In order to have your models be either an actor, target, or action object they
must first be registered with actstream. In v0.5 and above, actstream has a
registry of all actionable model classes. When you register them, actstream
sets up certain GenericRelations that are required for generating activity
streams.

Register your models with actstream in your
`AppConfig <https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications>`_.

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

Update these settings in your project's ``settings.py``. All settings are
contained inside the ``ACTSTREAM_SETTINGS`` dictionary. Here is an example of
what you can set in your ``settings.py``:

.. code-block:: python

    ACTSTREAM_SETTINGS = {
        'MANAGER': 'myapp.managers.MyActionManager',
        'FETCH_RELATIONS': True,
        'USE_JSONFIELD': True,
    }


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


USE_JSONFIELD
*************

Set this setting to ``True`` to enable the ``Action.data`` JSONField for all actions.
Lets you add custom data to any of your actions, see :ref:`custom-data`

Defaults to ``False``


ACTSTREAM_ACTION_MODEL
**********************

This setting allows users to swap the default action model used throughout
this package with one of their own. Set this setting to a
``'app_label.model_name'`` string pointing to your own model to override the
default action model used. Your model should inherit from the abstract
`AbstractAction` model.

Defaults to ``'actstream.Action'``.

ACTSTREAM_FOLLOW_MODEL
**********************

Similar to the previous setting, this setting allows users to swap the default
follow model with one of their own. Set this setting to a
``'app_label.model_name'`` string of your choosing to override the default
follow model used. Your model should inherit from the abstract `AbstractFollow`
model.

Defaults to ``'actstream.Follow'``.
