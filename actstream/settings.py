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
