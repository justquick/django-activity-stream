'''

django-activity-stream offered support for an optional JSON data field from 0.4.4 up until 1.4.0.
This was accomplished by overloading DataField with different model field types.
As of Django 3.2, the JSONField is supported by default.
However we need to keep this mapping to not break migrations.

'''
from django.db.models import JSONField

from actstream.settings import USE_JSONFIELD


__all__ = ('DataField', )


DataField = JSONField
