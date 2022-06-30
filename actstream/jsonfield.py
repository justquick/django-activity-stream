'''

Decide on a JSONField implementation based on available packages.

These are the options:
  - With recent Django >= 3.1 use Django's builtin JSONField.
  - For Django versions < 3.1 we need django-jsonfield-backport
      and will use its JSONField instead.

Raises an ImportError if USE_JSONFIELD is True, but none of the above 
apply.

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
