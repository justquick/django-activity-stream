from collections import OrderedDict

import django
from django.apps import apps
from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import pre_delete

from actstream import settings as actstream_settings
from actstream.signals import action


class ActstreamConfig(AppConfig):
    name = 'actstream'
    default_auto_field = 'django.db.models.AutoField'
    verbose_name = 'Activity Streams'

    def ready(self):
        from actstream.actions import action_handler
        action.connect(action_handler, dispatch_uid='actstream.models')
        action_class = self.get_model('action')

        if actstream_settings.USE_JSONFIELD:
            if not hasattr(action_class, 'data'):
                from actstream.jsonfield import DataField
                DataField(blank=True, null=True).contribute_to_class(
                    action_class, 'data'
                )

        from actstream.follows import delete_orphaned_follows
        pre_delete.connect(delete_orphaned_follows)
