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
from collections import namedtuple

from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from actstream.settings import USE_JSONFIELD


__all__ = ('DataField', 'register_app')

JSONFieldImport = namedtuple('JSONFieldImport', ['field_import', 'register_app_import'])

def register_app(app):
    """Noop unless django-jsonfield-compat overwrites it."""
    pass


DataField = models.TextField

possible_imports = [
    JSONFieldImport('django.db.models.JSONField', None),
    JSONFieldImport('jsonfield_compat.JSONField', 'jsonfield_compat.register_app'),
    JSONFieldImport('django_mysql.models.JSONField', None)
]

if USE_JSONFIELD:
    for possible_import in possible_imports:
        module, register_app_import = possible_import
        try:
            item = import_string(module)
            DataField = item
            if register_app_import:
                register_app = import_string(register_app_import)
            break
        except ImportError:
            pass
    
    raise ImproperlyConfigured(
        "You must either install django-jsonfield + "
        "django-jsonfield-compat, or django-mysql as an "
        "alternative, if you wish to use a JSONField on your "
        "actions"
    )
