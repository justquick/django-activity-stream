.. _drf:

Django ReST Framework Integration
=================================

As of version 2.0.0, django-activity-stream now supports integration with `Django ReST Framework <https://www.django-rest-framework.org/>`_.

DRF provides a standardized way of interacting with models stored in Django. It provides standard create/update/get operations using http standard methods.

Now with added DRF support, actstream models are hooked up to resources you can use with a standard API spec. 

Features
------------

Access actions
Follow/unfollow actors
Embed actor/target/action object as nested payloads in responses
Control the viesets/serializers/fields for other resources that are used when rendering the API

Settings
-------------
.. _drf-conf:

There are several parameters that you are able to set to control how django-activity-stream handles DRF integration. 
You are able to customize or mixin the classes that DRF relies on to create the API resources. You

The integration lets you customize the behavior of the following DRF objects:

- `Serializers <https://www.django-rest-framework.org/api-guide/serializers/#serializers>`_
- `ViewSets <https://www.django-rest-framework.org/api-guide/viewsets/#viewsets>`_
- `Permissions <https://www.django-rest-framework.org/api-guide/permissions/>`_
- `Model Fields <https://www.django-rest-framework.org/api-guide/serializers/#specifying-which-fields-to-include>`_

Simply modify the `DRF` section of `ACTSTREAM_SETTINGS` to include a custom class for the component you want to customize.
The configuration is specific to each app/model pair.
You must have these app/models registered with actstream before configuring.

.. code-block:: python

    ACTSTREAM_SETTINGS = {
        ...
        'DRF': {
            'SERIALIZERS': {
                'auth.Group': 'testapp.drf.GroupSerializer',
            },
            'VIEWSETS': {
                'auth.Group': 'testapp.drf.GroupViewSet'
            },
            'PERMISSIONS': {
                'testapp.MyUser': ['rest_framework.permissions.IsAdminUser']
            },
            'MODEL_FIELDS': {
                'sites.Site': ['id', 'domain']
            }
        }
    }