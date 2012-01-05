from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured


class ModelNotActionable(ImproperlyConfigured):
    """
    Raised when a Model not in ``ACTSTREAM_ACTION_MODELS`` setting is used in
    an Action.
    """

    def __str__(self):
        model = self.args[0]
        if not issubclass(model, ModelBase):
            return 'Object %r must be a Django Model not %s' % (model,
                type(model))
        opts = model._meta
        return 'Model %s not recognized, add "%s.%s" to '\
            'ACTSTREAM_ACTION_MODELS' % (model.__name__, opts.app_label,
                opts.module_name)


class BadQuerySet(ValueError):
    """
    Action stream must return a QuerySet of Action items.
    """


def check_actionable_model(model):
    """
    If the model is not defined in the ``MODELS`` setting this check raises the
    ``ModelNotActionable`` exception.
    """
    from actstream.settings import MODELS

    model = model if hasattr(model, 'objects') else model.__class__
    if not model in MODELS.values():
        raise ModelNotActionable(model)
