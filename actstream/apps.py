from django.core.exceptions import ImproperlyConfigured

from actstream import settings
from actstream.signals import action
from actstream.compat_apps import AppConfig


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
                                           'or Django>=1.9 installed (with native postgres JSONField support), '
                                           'if you wish to use a JSONField on your actions')
            JSONField(blank=True, null=True).contribute_to_class(action_class, 'data')
