import django
from django.conf import settings


SETTINGS = getattr(settings, 'ACTSTREAM_SETTINGS', {})


def get_action_manager():
    """
    Returns the class of the action manager to use from ACTSTREAM_SETTINGS['MANAGER']
    """
    mod = SETTINGS.get('MANAGER', 'actstream.managers.ActionManager')
    a, j = mod.split('.'), lambda l: '.'.join(l)
    try:
        return getattr(__import__(j(a[:-1]), {}, {}, [a[-1]]), a[-1])()
    except ImportError:
        raise ImportError('Cannot import %s try fixing ACTSTREAM_SETTINGS[MANAGER]'
                          'setting.' % mod)

USE_PREFETCH = SETTINGS.get('USE_PREFETCH',
                            django.VERSION >= (1, 4))

FETCH_RELATIONS = SETTINGS.get('FETCH_RELATIONS', True)

GFK_FETCH_DEPTH = SETTINGS.get('GFK_FETCH_DEPTH', 0)

USE_JSONFIELD = SETTINGS.get('USE_JSONFIELD', False)
