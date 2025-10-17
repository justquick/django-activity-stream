from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


SETTINGS = getattr(settings, 'ACTSTREAM_SETTINGS', {})


def import_obj(mod):
    mod_path = mod.split('.')
    try:
        obj = __import__('.'.join(mod_path[:-1]), {}, {}, [mod_path[-1]])
        return getattr(obj, mod_path[-1])
    except:
        raise ImportError(f'Cannot import: {mod}')


def get_action_manager():
    """
    Returns the class of the action manager to use from ACTSTREAM_SETTINGS['MANAGER']
    """
    mod = SETTINGS.get('MANAGER', 'actstream.managers.ActionManager')
    try:
        return import_obj(mod)()
    except ImportError:
        raise ImproperlyConfigured(f'Cannot import {mod} try fixing ACTSTREAM_SETTINGS[MANAGER] setting.')


FETCH_RELATIONS = SETTINGS.get('FETCH_RELATIONS', True)

USE_JSONFIELD = SETTINGS.get('USE_JSONFIELD', False)

USE_DRF = 'DRF' in SETTINGS

DRF_SETTINGS = {
    'ENABLE': False,
    'EXPAND_FIELDS': True,
    'HYPERLINK_FIELDS': False,
    'SERIALIZERS': {},
    'MODEL_FIELDS': {},
    'VIEWSETS': {},
    'PERMISSIONS': ['rest_framework.permissions.IsAuthenticated']
}

if USE_DRF:
    DRF_SETTINGS.update(SETTINGS.get('DRF', {}))

    for item in ('SERIALIZERS', 'VIEWSETS', 'MODEL_FIELDS'):
        DRF_SETTINGS[item] = {
            label.lower(): obj for label, obj in DRF_SETTINGS[item].items()
        }


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
