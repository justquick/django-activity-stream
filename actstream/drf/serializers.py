from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from actstream.models import Follow, Action
from actstream.registry import registry
from actstream.settings import DRF_SETTINGS, import_obj


class ExpandRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return registered_serializers[value.__class__](value).data


DEFAULT_SERIALIZER = serializers.ModelSerializer


def serializer_factory(model_class, **meta_opts):
    model_label = f'{model_class._meta.app_label}.{model_class._meta.model_name}'
    model_attrs = DRF_SETTINGS['MODEL_FIELDS'].get(model_label, {'fields': '__all__'})
    model_attrs['model'] = model_class
    meta_class = type('Meta', (), model_attrs)
    serializer_class = DEFAULT_SERIALIZER
    if model_label in DRF_SETTINGS['SERIALIZERS']:
        serializer_class = import_obj(DRF_SETTINGS['SERIALIZERS'][model_label])
    return type(f'{model_class.__name__}Serializer', (serializer_class,), {'Meta': meta_class})


def related_field_factory(model_class, queryset=None):
    if queryset is None:
        queryset = model_class.objects.all()
    related_field_class = serializers.PrimaryKeyRelatedField
    kwargs = {'queryset': queryset}
    if DRF_SETTINGS['HYPERLINK_FIELDS']:
        related_field_class = serializers.HyperlinkedRelatedField
        kwargs['view_name'] = f'{model_class.__name__.lower()}-detail'
    elif DRF_SETTINGS['EXPAND_FIELDS']:
        related_field_class = ExpandRelatedField
    field = type(f'{model_class.__name__}RelatedField', (related_field_class,), {})
    return field(**kwargs)  # , )


def registry_factory(factory):
    return {model_class: factory(model_class) for model_class in registry}


def GRF():
    return GenericRelatedField(registry_factory(related_field_factory))


registered_serializers = registry_factory(serializer_factory)


class ActionSerializer(serializers.ModelSerializer):
    actor = GRF()
    target = GRF()
    action_object = GRF()

    class Meta:
        model = Action
        fields = ['id', 'verb', 'description', 'timestamp', 'actor', 'target', 'action_object']


class FollowSerializer(serializers.ModelSerializer):
    user = GRF()
    follow_object = GRF()

    class Meta:
        model = Follow
        fields = ['id', 'flag', 'user', 'follow_object', 'started', 'actor_only']
