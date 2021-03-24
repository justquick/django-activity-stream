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


def get_swappable_model(model):
    model_lookup = getattr(settings, 'ACTSTREAM_%s_MODEL' % model.upper(), 'actstream.%s' % model)
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


def get_follow_model():
    """Return the Follow model that is active."""
    return get_swappable_model('Follow')


def get_action_model():
    """Return the Action model that is active."""
    return get_swappable_model('Action')
