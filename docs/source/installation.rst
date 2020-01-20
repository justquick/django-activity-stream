Installation
============

Get the code
------------

Installation is easy using ``pip`` and the only requirement is a recent version of Django.

.. code-block:: bash

    $ pip install django-activity-stream

or get it from source

.. code-block:: bash

    $ pip install git+https://github.com/justquick/django-activity-stream.git#egg=actstream


Basic app configuration
-----------------------

Then to add the Django Activity Stream to your project add the app ``actstream``  and ``django.contib.sites`` to your ``INSTALLED_APPS`` and urlconf. In addition to, add the setting ``SITE_ID = 1`` below the installed apps.


.. code-block:: python

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.sites',
        ...
        'actstream'
    )

    SITE_ID = 1

Add the activity urls to your urlconf

.. code-block:: python

    urlpatterns = [
        ...
        ('^activity/', include('actstream.urls')),
        ...
    ]

The activity urls are not required for basic usage but provide activity :ref:`feeds` and handle following, unfollowing and querying of followers.


Add extra data to actions
-------------------------

If you want to use custom data on your actions, then make sure you have `django-jsonfield <https://pypi.org/project/django-jsonfield/>`_ installed

.. code-block:: bash

    $ pip install django-activity-stream[jsonfield]

You can learn more at :ref:`custom-data`


Supported Environments
----------------------

The following Python/Django versions and database configurations are supported by django-activity-stream.
Make sure to pick the version of Django and django-activity-stream that supports the environment you are using.

.. note::

    For Django compatibility details, `read the Django docs <https://docs.djangoproject.com/en/1.9/faq/install/#what-python-version-can-i-use-with-django>`_.
    For django-activity-stream compatibility details, see the :ref:`changelog`.

Python
******

* **Python 2**: 2.7
* **Python 3**: 3.4, 3.5 and 3.6
* **PyPy**: 2 and 3

Django
******

* **Django**: 1.11, 2.0 and 2.1

Databases
*********

django-activity-stream has been tested to work with the following databases but may work on other platforms (YMMV)

* **Sqlite**: 3
* **PostgreSQL**: 9.3+
    * Python: `psycopg2 <http://initd.org/psycopg/docs/>`_
    * PyPy: `psycopg2cffi <https://github.com/chtd/psycopg2cffi>`_
* **MySQL**: 5.5 and 5.6+
    * Python/PyPy: `MySQL-python <https://github.com/farcepest/MySQLdb1>`_
    * Python 3: `PyMySQL <https://github.com/PyMySQL/PyMySQL/>`_
