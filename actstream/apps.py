from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

from actstream import get_action_model, settings
from actstream.signals import action


class ActstreamConfig(AppConfig):
    name = 'actstream'

    def ready(self):
        from actstream.actions import action_handler
        action.connect(action_handler, dispatch_uid='actstream.models')
        action_class = get_action_model()

        if settings.USE_JSONFIELD:
            try:
                from jsonfield_compat import JSONField, register_app
            except ImportError:
                raise ImproperlyConfigured(
                    'You must have django-jsonfield and django-jsonfield-compat '
                    'installed if you wish to use a JSONField on your actions'
                )
            JSONField(blank=True, null=True).contribute_to_class(action_class, 'data')
            register_app(self)
