from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


SETTINGS = getattr(settings, 'ACTSTREAM_SETTINGS', {})


def import_obj(mod):
    mod_path = mod.split('.')
    return getattr(__import__('.'.join(mod_path[:-1]), {}, {}, [mod_path[-1]]), mod_path[-1])


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

DRF_SETTINGS = SETTINGS.get('DRF', {})

DRF_DEFAULTS = {
    'ENABLE': False,
    'EXPAND_FIELDS': False,
    'HYPERLINK_FIELDS': True,
    'SERIALIZERS': {},
    'VIEWSETS': {}
}
for name, value in DRF_DEFAULTS.items():
    DRF_SETTINGS.setdefault(name, value)

USE_DRF = DRF_SETTINGS['ENABLE']

for item in ('SERIALIZERS', 'VIEWSETS'):
    DRF_SETTINGS[item] = {
        label.lower(): obj for label, obj in DRF_SETTINGS[item].items()
    }
