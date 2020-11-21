from functools import lru_cache

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


SETTINGS = getattr(settings, 'ACTSTREAM_SETTINGS', {})


def get_action_manager():
    """
    Returns the class of the action manager to use from ACTSTREAM_SETTINGS['MANAGER']
    """
    mod = SETTINGS.get('MANAGER', 'actstream.managers.ActionManager')
    mod_path = mod.split('.')
    try:
        return getattr(__import__('.'.join(mod_path[:-1]), {}, {},
                                  [mod_path[-1]]), mod_path[-1])()
    except ImportError:
        raise ImportError(
            'Cannot import %s try fixing ACTSTREAM_SETTINGS[MANAGER]'
            'setting.' % mod
        )


FETCH_RELATIONS = SETTINGS.get('FETCH_RELATIONS', True)

USE_JSONFIELD = SETTINGS.get('USE_JSONFIELD', False)

FOLLOW_MODEL = SETTINGS.get('ACTSTREAM_FOLLOW_MODEL', 'actstream.Follow')
ACTION_MODEL = SETTINGS.get('ACTSTREAM_ACTION_MODEL', 'actstream.Action')


def get_swappable_model(model_lookup):
    try:
        return apps.get_model(model_lookup, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "%s must be of the form 'app_label.model_name'" % model_lookup
        )
    except LookupError:
        raise ImproperlyConfigured(
            "Model '%s' has not been installed" % model_lookup
        )


@lru_cache(maxsize=None)
def get_follow_model():
    """Return the Follow model that is active."""
    return get_swappable_model(FOLLOW_MODEL)


@lru_cache(maxsize=None)
def get_action_model():
    """Return the Action model that is active."""
    return get_swappable_model(ACTION_MODEL)
