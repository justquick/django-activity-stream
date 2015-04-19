"""
Django>=1.5 compatibility utilities
"""

from django.conf import settings

user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
username_field = lambda: getattr(get_user_model(), 'USERNAME_FIELD', 'username')

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_unicode as smart_text

try:
    from django.contrib.contenttypes import fields as generic
except ImportError:
    from django.contrib.contenttypes import generic

try:
    from django.apps import AppConfig
    user_model_class = lambda: AppConfig.get_model(*user_model_label.split('.'))
except ImportError:
    from django.db import models
    user_model_class = lambda: models.get_model(*user_model_label.split('.'))

    class AppConfig(object):
        name = None

        def get_model(self, model_name):
            return models.get_model(self.name.split('.')[-1], model_name, only_installed=False)
