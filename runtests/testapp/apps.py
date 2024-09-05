from django.apps import AppConfig, apps


class TestappConfig(AppConfig):
    name = 'testapp'

    def ready(self):
        from actstream.registry import register
        register(apps.get_model('auth', 'group'))
        register(apps.get_model('sites', 'site'))
        register(self.get_model('player'))
        myuser = self.get_model('myuser')
        if myuser:
            register(myuser)
