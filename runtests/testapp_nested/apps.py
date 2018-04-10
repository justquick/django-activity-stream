from django.apps import AppConfig


class TestappNestedConfig(AppConfig):
    name = 'testapp_nested'

    def ready(self):
        from actstream.registry import register
        register(self.get_model('nestedmodel'))
