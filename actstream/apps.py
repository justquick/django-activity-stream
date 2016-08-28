from django.core.exceptions import ImproperlyConfigured

from actstream import settings
from actstream.signals import action
from actstream.compat_apps import AppConfig


class ActstreamConfig(AppConfig):
    name = 'actstream'

    def ready(self):
        from actstream.actions import action_handler
        action.connect(action_handler, dispatch_uid='actstream.models')
