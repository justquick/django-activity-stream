from django.conf import settings
from django.db.models import get_model

MODELS = {}
for model in getattr(settings, 'ACTSTREAM_ACTION_MODELS', ('auth.User',)):
    MODELS[model.lower()] = model = get_model(*model.split('.'))

MANAGER_MODULE = getattr(settings, 'ACTSTREAM_MANAGER',
    'actstream.managers.ActionManager')
a, j = MANAGER_MODULE.split('.'), lambda l: '.'.join(l)
MANAGER_MODULE = getattr(__import__(j(a[:-1]), {}, {}, [a[-1]]), a[-1])
