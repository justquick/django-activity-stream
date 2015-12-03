try:
    from django.apps import AppConfig
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models import get_model

    class AppConfig(object):
        name = None

        def get_model(self, model_name):
            return get_model(self.name.split('.')[-1], model_name, only_installed=False)
