try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object


class TestappConfig(AppConfig):
    name = 'testapp'

    def ready(self):
        from actstream.registry import register
        register(self.get_model('player'), self.get_model('myuser'))
