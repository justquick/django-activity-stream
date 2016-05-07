from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text

from actstream import settings
from actstream.signals import action
from actstream.compat_apps import AppConfig

try:
    from django.db.backends.mysql.base import DatabaseOperations
except (ImportError, ImproperlyConfigured):
    DatabaseOperations = None


def fixed_last_executed_query(self, cursor, sql, params):
    """
    Patches error with MySQL + Django<=1.5: https://code.djangoproject.com/ticket/19954
    """
    return force_text(cursor._last_executed, errors='replace')


class ActstreamConfig(AppConfig):
    name = 'actstream'

    def ready(self):
        from actstream.actions import action_handler
        from actstream.compat import JSONField
        action.connect(action_handler, dispatch_uid='actstream.models')
        action_class = self.get_model('action')

        if settings.USE_JSONFIELD:
            if JSONField is None:
                raise ImproperlyConfigured('You must have either django-jsonfield installed, '
                                           'or Django>=1.8 installed (with native postgres JSONField support), '
                                           'if you wish to use a JSONField on your actions')
            JSONField(blank=True, null=True).contribute_to_class(action_class, 'data')

        if DatabaseOperations:
            DatabaseOperations.last_executed_query = fixed_last_executed_query
