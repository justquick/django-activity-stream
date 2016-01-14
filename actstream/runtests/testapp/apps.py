from actstream.compat_apps import AppConfig


class TestappConfig(AppConfig):
    name = 'actstream.runtests.testapp'

    def ready(self):
        from actstream.registry import register
        register(self.get_model('player'))
        myuser = self.get_model('myuser')
        if myuser:
            register(myuser)
