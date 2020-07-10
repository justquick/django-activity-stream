from django.apps import AppConfig

from actstream import settings
from actstream.signals import action


class ActstreamConfig(AppConfig):
    name = 'actstream'

    def ready(self):
        from actstream.actions import action_handler
        action.connect(action_handler, dispatch_uid='actstream.models')
        action_class = self.get_model('action')

        if settings.USE_JSONFIELD and not hasattr(action_class, 'data'):
            from actstream.jsonfield import DataField, register_app
            DataField(blank=True, null=True).contribute_to_class(
                action_class, 'data'
            )
            register_app(self)
