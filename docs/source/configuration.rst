Configuration
==============

Update these settings in your project's ``settings.py``.
As of v0.4.4, all settings are contained inside the ``ACTSTREAM_SETTINGS`` dictionary.
Here is an example of what you can set in your ``settings.py``::

    ACTSTREAM_SETTINGS = {
        'MODELS': ('auth.user', 'auth.group', 'sites.site', 'comments.comment'),
        'MANAGER': 'myapp.streams.MyActionManager',
        'FETCH_RELATIONS': True,
        'USE_PREFETCH': True,
        'USE_JSONFIELD': True,
        'GFK_FETCH_DEPTH': 1,
    }


Supported settings are defined below.

MODELS
*******

A list the models that you want to enable actions for. Models must be in the format ``app_label.model_name`` .
In the background, django-activity-stream sets up ``GenericRelations`` to handle stream generation.

Defaults to ``('auth.user',)``


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
