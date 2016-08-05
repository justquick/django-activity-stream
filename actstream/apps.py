from django.core.exceptions import ImproperlyConfigured

from actstream import settings
from actstream.compat_apps import AppConfig
from actstream.signals import action


class ActstreamConfig(AppConfig):
    name = 'actstream'

    def ready(self):
        from actstream.actions import action_handler
        action.connect(action_handler, dispatch_uid='actstream.models')
        action_class = self.get_model('action')

        if settings.USE_JSONFIELD:
            try:
                from jsonfield.fields import JSONField
            except ImportError:
                raise ImproperlyConfigured('You must have django-jsonfield installed '
                                           'if you wish to use a JSONField on your actions')
            JSONField(blank=True, null=True).contribute_to_class(action_class, 'data')
