from django.conf import settings


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
