from django.conf import settings
from django.db.models import get_model
from django.db.models.signals import class_prepared

ACTSTREAM_ACTION_MODELS = [m.lower() for m in getattr(settings,
    'ACTSTREAM_ACTION_MODELS', ('auth.User',))]

MODELS = {}

# Certain application configurations can lead to models not being available
# to get_model at import time. To overcome this problem, we register a
# class_prepared listener. This needs to be done before we do the initial
# population of MODELS, since we cannot predict what is already available,
# what will be available later, and what will be discovered during model
# loading.
def late_registration(sender, **kwargs):
    opts = sender._meta
    key = "%s.%s" % (opts.app_label,opts.module_name)
    if key in ACTSTREAM_ACTION_MODELS:
        MODELS[key] = sender
class_prepared.connect(late_registration)

for model in ACTSTREAM_ACTION_MODELS:
    MODELS[model.lower()] = model = get_model(*model.split('.'))

MANAGER_MODULE = getattr(settings, 'ACTSTREAM_MANAGER',
    'actstream.managers.ActionManager')
a, j = MANAGER_MODULE.split('.'), lambda l: '.'.join(l)
MANAGER_MODULE = getattr(__import__(j(a[:-1]), {}, {}, [a[-1]]), a[-1])
