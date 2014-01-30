from django.apps import AppConfig


class ActstreamConfig(AppConfig):
    name = 'actstream'

    def ready(self):
        from actstream.models import setup_generic_relations
        setup_generic_relations()
