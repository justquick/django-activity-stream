from django.core.exceptions import ImproperlyConfigured

from actstream.settings import MODELS

class ModelNotActionable(ImproperlyConfigured):
    """
    Raised when a Model not in ACTSTREAM_ACTION_MODELS is used in an Action
    """
    def __str__(self):
        model = self.args[0]
        opts = model._meta
        return 'Model %s.%s not recognized, add "%s.%s" to ACTSTREAM_ACTION_MODELS' % (
            opts.app_label, model.__class__.__name__, opts.app_label, opts.module_name)

def check_actionable_model(model):
    """
    If the model is not defined in MODELS this check raises ModelNotActionable
    """
    if not model.__class__ in MODELS:
        raise ModelNotActionable(model)