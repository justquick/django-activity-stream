'''

Decide on a JSONField implementation based on available packages.

There are two possible options, preferred in the following order:
  - JSONField from django-jsonfield with django-jsonfield-compat
  - JSONField from django-mysql (needs MySQL 5.7+)

Raises an ImportError if USE_JSONFIELD is True but none of these are
installed.

Falls back to a simple Django TextField if USE_JSONFIELD is False,
however that field will be removed by migration 0002 directly
afterwards.

'''
from django.db import models
from django.core.exceptions import ImproperlyConfigured

from actstream.settings import USE_JSONFIELD


__all__ = ('DataField', 'register_app')


def register_app(app):
    """Noop unless django-jsonfield-compat overwrites it."""
    pass


DataField = models.TextField

if USE_JSONFIELD:
    try:
        from jsonfield_compat import JSONField, register_app
        DataField = JSONField
    except ImportError as err:
        try:
            from django_mysql.models import JSONField
            DataField = JSONField

        except ImportError:
            raise ImproperlyConfigured(
                'You must either install django-jsonfield + '
                'django-jsonfield-compat, or django-mysql as an '
                'alternative, if you wish to use a JSONField on your '
                'actions'
            )
