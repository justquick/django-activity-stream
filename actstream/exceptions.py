from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured

from actstream.settings import get_models


class ModelNotActionable(ImproperlyConfigured):
    """
    Raised when a Model not in ``ACTSTREAM_ACTION_MODELS`` setting is used in
    an Action.
    """

    def __str__(self):
        model = self.args[0]
        if not is_model(model):
            return 'Object %r must be a Django Model not %s' % (model,
                type(model))
        opts = model._meta
        return 'Model %s not recognized, add "%s.%s" to the ACTSTREAM_SETTINGS["MODELS"] settings' % (
            model.__name__, opts.app_label, opts.module_name)


class BadQuerySet(ValueError):
    """
    Action stream must return a QuerySet of Action items.
    """

def is_model(obj):
    """
    Returns True if the obj is a Django model
    """
    if not hasattr(obj, '_meta'):
        return False
    if not hasattr(obj._meta, 'db_table'):
        return False
    return True

def check_actionable_model(model):
    """
    If the model is not defined in the ``MODELS`` setting this check raises the
    ``ModelNotActionable`` exception.
    """
    model = model if hasattr(model, 'objects') else model.__class__
    if not model in get_models().values():
        raise ModelNotActionable(model)
