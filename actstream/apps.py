from collections import OrderedDict

import django
from django.apps import apps
from django.apps import AppConfig
from django.conf import settings

from actstream import settings as actstream_settings
from actstream.signals import action


class ActstreamConfig(AppConfig):
    name = 'actstream'
    default_auto_field = 'django.db.models.AutoField'
    verbose_name = 'Activity Streams'

    def ready(self):
        from actstream.actions import action_handler
        action.connect(action_handler, dispatch_uid='actstream.models')
        action_class = actstream_settings.get_action_model()

        if actstream_settings.USE_JSONFIELD:
            if not hasattr(action_class, 'data'):
                from actstream.jsonfield import DataField
                DataField(blank=True, null=True).contribute_to_class(
                    action_class, 'data'
                )

            # dynamically load django_jsonfield_backport to INSTALLED_APPS
            if django.VERSION < (3, 1) and 'django_jsonfield_backport' not in settings.INSTALLED_APPS:
                settings.INSTALLED_APPS += ('django_jsonfield_backport', )
                # reset loaded apps
                apps.app_configs = OrderedDict()
                # reset initialization status
                apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
                apps.clear_cache()
                # re-initialize all apps
                apps.populate(settings.INSTALLED_APPS)
