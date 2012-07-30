Installation
============

Installation is easy using ``pip`` and the only requirement is a recent version of Django.

.. code-block:: bash

    $ pip install django-activity-stream

or get it from source

.. code-block:: bash

    $ git clone https://justquick@github.com/justquick/django-activity-stream.git
    $ cd django-activity-stream
    $ python setup.py install

Then to add the Django Activity Stream to your project add the app ``actstream`` to your ``INSTALLED_APPS`` and urlconf.

The app should go somewhere after all the apps that are going to be generating activities like ``django.contrib.auth``::

    INSTALLED_APPS = (
        'django.contrib.auth',
        ...
        'actstream',
        ...
    )

Add the activity urls to your urlconf::

    urlpatterns = patterns('',
        ...
        ('^activity/', include('actstream.urls')),
        ...
    )

If you want to use custom data on your actions, then make sure you have `django-jsonfield <https://github.com/bradjasper/django-jsonfield/>`_ installed::

    pip install django-jsonfield

You can learn more at :ref:`custom-data`
