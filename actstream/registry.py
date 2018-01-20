from inspect import isclass
import re

import django
from django.conf import settings
from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured
from django.utils.six import string_types


from actstream.compat import generic, get_model


class RegistrationError(Exception):
    pass


def setup_generic_relations(model_class):
    """
    Set up GenericRelations for actionable models.
    """
    Action = get_model('actstream', 'action')

    if Action is None:
        raise RegistrationError(
            'Unable get actstream.Action. Potential circular imports '
            'in initialisation. Try moving actstream app to come after the '
            'apps which have models to register in the INSTALLED_APPS setting.'
        )

    related_attr_name = 'related_name'
    related_attr_value = 'actions_with_%s' % label(model_class)
    if django.VERSION[:2] >= (1, 8):
        related_attr_name = 'related_query_name'
    relations = {}
    for field in ('actor', 'target', 'action_object'):
        attr = '%s_actions' % field
        attr_value = '%s_as_%s' % (related_attr_value, field)
        kwargs = {
            'content_type_field': '%s_content_type' % field,
            'object_id_field': '%s_object_id' % field,
            related_attr_name: attr_value
        }
        rel = generic.GenericRelation('actstream.Action', **kwargs)
        rel.contribute_to_class(model_class, attr)
        relations[field] = rel

        # @@@ I'm not entirely sure why this works
        setattr(Action, attr_value, None)
    return relations


def label(model_class):
    if hasattr(model_class._meta, 'model_name'):
        model_name = model_class._meta.model_name
    else:
        model_name = model_class._meta.module_name
    return '%s_%s' % (model_class._meta.app_label, model_name)


def is_installed(model_class):
    """
    Returns True if a model_class is installed.
    model_class._meta.installed is only reliable in Django 1.7+
    """
    if django.VERSION[:2] >= (1, 8):
        return model_class._meta.installed
    if model_class._meta.app_label in settings.INSTALLED_APPS:
        return True
    return re.sub(r'\.models.*$', '', model_class.__module__) in settings.INSTALLED_APPS


def validate(model_class, exception_class=ImproperlyConfigured):
    if isinstance(model_class, string_types):
        model_class = get_model(*model_class.split('.'))
    if not isinstance(model_class, ModelBase):
        raise exception_class(
            'Object %r is not a Model class.' % model_class)
    if model_class._meta.abstract:
        raise exception_class(
            'The model %r is abstract, so it cannot be registered with '
            'actstream.' % model_class)
    if not is_installed(model_class):
        raise exception_class(
            'The model %r is not installed, please put the app "%s" in your '
            'INSTALLED_APPS setting.' % (model_class,
                                         model_class._meta.app_label))
    return model_class


class ActionableModelRegistry(dict):

    def register(self, *model_classes_or_labels):
        for class_or_label in model_classes_or_labels:
            model_class = validate(class_or_label)
            if model_class not in self:
                self[model_class] = setup_generic_relations(model_class)

    def unregister(self, *model_classes_or_labels):
        for class_or_label in model_classes_or_labels:
            model_class = validate(class_or_label)
            if model_class in self:
                del self[model_class]

    def check(self, model_class_or_object):
        if getattr(model_class_or_object, '_deferred', None):
            model_class_or_object = model_class_or_object._meta.proxy_for_model
        if not isclass(model_class_or_object):
            model_class_or_object = model_class_or_object.__class__
        model_class = validate(model_class_or_object, RuntimeError)
        if model_class not in self:
            raise ImproperlyConfigured(
                'The model %s is not registered. Please use actstream.registry '
                'to register it.' % model_class.__name__)

registry = ActionableModelRegistry()
register = registry.register
unregister = registry.unregister
check = registry.check
