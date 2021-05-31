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
import django
from django.db import models
from django.core.exceptions import ImproperlyConfigured

from actstream.settings import USE_JSONFIELD


__all__ = ('DataField', )


DataField = models.TextField

if USE_JSONFIELD:
    if django.VERSION >= (3, 1):
        from django.db.models import JSONField
        DataField = JSONField
    else:
        try:
            from django_jsonfield_backport.models import JSONField
            DataField = JSONField
        except ImportError:
            raise ImproperlyConfigured(
                'You must install django-jsonfield-backport, '
                'if you wish to use a JSONField on your actions '
                'and run Django < 3.1'
            )
