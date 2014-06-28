try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object

from actstream.registry import register


class TestappConfig(AppConfig):
    name = 'testapp'

    def ready(self):
        register(self.get_model('player'), self.get_model('myuser'))
