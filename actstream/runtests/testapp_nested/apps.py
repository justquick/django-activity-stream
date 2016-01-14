from actstream.compat_apps import AppConfig


class TestappNestedConfig(AppConfig):
    name = 'actstream.runtests.testapp_nested'

    def ready(self):
        from actstream.registry import register
        register(self.get_model('nestedmodel'))
