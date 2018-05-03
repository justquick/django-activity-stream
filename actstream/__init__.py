from django.apps import apps as django_apps
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

try:
    from actstream.signals import action
except ImportError:
    pass

__version__ = '0.7.0'
__author__ = 'Justin Quick <justquick@gmail.com>'
default_app_config = 'actstream.apps.ActstreamConfig'


def get_swappable_model(model_setting, default):
    model_lookup = getattr(django_settings, model_setting, default)
    try:
        return django_apps.get_model(model_lookup, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "%s must be of the form 'app_label.model_name'" % model_setting
        )
    except LookupError:
        raise ImproperlyConfigured(
            "%s refers to model '%s' that has not been installed" % (model_setting, model_lookup)
        )


def get_follow_model():
    """Return the Follow model that is active."""
    return get_swappable_model('ACTSTREAM_FOLLOW_MODEL', 'actstream.Follow')


def get_action_model():
    """Return the Action model that is active."""
    return get_swappable_model('ACTSTREAM_ACTION_MODEL', 'actstream.Action')
