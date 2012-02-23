Configuration
==============

Update these settings in your project's ``settings.py``.  Supported settings are defined below.

Action Models
*************

``ACTSTREAM_ACTION_MODELS = ['auth.User']``

A list the models that you want to enable actions for. Models must be in the format ``app_label.model_name`` .
In the background, django-activity-stream sets up ``GenericRelations`` to handle stream generation.


Stream Modules
**************

``ACTSTREAM_MANAGER = 'actstream.managers.ActionManager'``

The name of the manager to use for ``Action.objects``.
Add your own manager here to create custom streams.

For more info, see :ref:`custom-streams`
