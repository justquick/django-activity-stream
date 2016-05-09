"""
Django>=1.5 compatibility utilities
"""

from django.conf import settings

user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
username_field = lambda: getattr(get_user_model(), 'USERNAME_FIELD', 'username')

try:
    is_postgres = 'postgres' in settings.DATABASES['default']['ENGINE']
except KeyError:
    is_postgres = False

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text

try:
    from django.contrib.contenttypes import fields as generic
except ImportError:
    from django.contrib.contenttypes import generic

try:
    from django.apps import AppConfig
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models import get_model

JSONField = None
if is_postgres:
    try:
        # Django >= 1.9 has native Postgres jsonb support
        from django.contrib.postgres.fields import JSONField
    except ImportError:
        pass
if JSONField is None:
    try:
        from jsonfield.fields import JSONField
    except ImportError:
        pass
