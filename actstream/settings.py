import django
from django.conf import settings
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from django.utils import importlib
from django.core.exceptions import ImproperlyConfigured



SETTINGS = getattr(settings, 'ACTSTREAM_SETTINGS', {})

def get_models():
    """
    Returns a lookup of 'app_label.model': <model class> from ACTSTREAM_SETTINGS['MODELS']
    Only call this right before you need to inspect the models
    """
    models = {}
    for model in SETTINGS.get('MODELS', ('auth.User',)):
        models[model.lower()] = get_model(*model.split('.'))
    return models

def get_action_manager():
    """
    Returns the class of the action manager to use from ACTSTREAM_SETTINGS['MANAGER']
    """
    mod = SETTINGS.get('MANAGER', 'actstream.managers.ActionManager')
    a, j = mod.split('.'), lambda l: '.'.join(l)
    return getattr(__import__(j(a[:-1]), {}, {}, [a[-1]]), a[-1])()

USE_PREFETCH = SETTINGS.get('USE_PREFETCH',
                            django.VERSION[0] == 1 and django.VERSION[1] >= 4)

FETCH_RELATIONS = SETTINGS.get('FETCH_RELATIONS', True)

GFK_FETCH_DEPTH = SETTINGS.get('GFK_FETCH_DEPTH', 0)

USE_JSONFIELD = SETTINGS.get('USE_JSONFIELD', False)

USE_JSONFIELD = SETTINGS.get('USE_JSONFIELD', False)

VERB_CHOICES_MODULE = SETTINGS.get('VERB_CHOICES_MODULE', 'actstream.verbs')

try:

    my_verbs = importlib.import_module(VERB_CHOICES_MODULE)
    VERB_CHOICES = my_verbs.VERB_CHOICES
    
    for v in VERB_CHOICES:
        if len([enum for enum, text in VERB_CHOICES if text == unicode(v[1])]) > 1:
            raise ImproperlyConfigured("Your list of Verbs (VERB_CHOICES) seems uncorrectly configured. You have twice the word \'%s\'." % (unicode(v[1]))) 
        if len([enum for enum, text in VERB_CHOICES if enum == v[0]]) > 1:
            raise ImproperlyConfigured("Your list of Verbs (VERB_CHOICES) seems uncorrectly configured. You have twice the index \'%s\'." % (v[0]))
    
except:
    raise ImproperlyConfigured("Your list of Verbs (VERB_CHOICES) is empty. Please configure 'VERB_CHOICES_MODULE' in ACTSTREAM_SETTINGS.")



