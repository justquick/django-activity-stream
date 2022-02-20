from django.conf import settings


SETTINGS = getattr(settings, 'ACTSTREAM_SETTINGS', {})


def import_obj(mod, msg=None):
    mod_path = mod.split('.')
    try:
        return getattr(__import__('.'.join(mod_path[:-1]), {}, {},
                                  [mod_path[-1]]), mod_path[-1])()
    except ImportError:
        raise ImportError(None)


def get_action_manager():
    """
    Returns the class of the action manager to use from ACTSTREAM_SETTINGS['MANAGER']
    """
    mod = SETTINGS.get('MANAGER', 'actstream.managers.ActionManager')
    return import_obj(mod, f'Cannot import {mod} try fixing ACTSTREAM_SETTINGS[MANAGER] setting.')


FETCH_RELATIONS = SETTINGS.get('FETCH_RELATIONS', True)

USE_JSONFIELD = SETTINGS.get('USE_JSONFIELD', False)

DRF_SETTINGS = SETTINGS.get('DRF', {})

DRF_DEFAULTS = {
    'EXPAND_FIELDS': False,
    'HYPERLINK_FIELDS': True,
    'SERIALIZERS': {},
    'VIEWSETS': {}
}
for name, value in DRF_DEFAULTS.items():
    DRF_SETTINGS.setdefault(name, value)
for model_class, serializer in DRF_DEFAULTS['SERIALIZERS']:
    DRF_DEFAULTS['SERIALIZERS'][model_class] = import_obj(serializer)
