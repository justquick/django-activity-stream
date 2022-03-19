from rest_framework import serializers
from generic_relations.relations import GenericRelatedField

from actstream.models import Follow, Action
from actstream.registry import registry, label
from actstream.settings import DRF_SETTINGS, import_obj


class ExpandRelatedField(serializers.RelatedField):
    """
    Expands related fields to use other Serializer. Similar to the AS1 JSON spec
    """
    def to_representation(self, value):
        return registered_serializers[value.__class__](value).data


DEFAULT_SERIALIZER = serializers.ModelSerializer


def serializer_factory(model_class):
    """
    Returns a subclass of `ModelSerializer` for each model_class in the registry
    """
    model_label = label(model_class).lower()
    if model_label in DRF_SETTINGS['SERIALIZERS']:
        return import_obj(DRF_SETTINGS['SERIALIZERS'][model_label])
    model_fields = DRF_SETTINGS['MODEL_FIELDS'].get(model_label, '__all__')
    meta_class = type('Meta', (), {'model': model_class, 'fields': model_fields})
    return type(f'{model_class.__name__}Serializer', (DEFAULT_SERIALIZER,), {'Meta': meta_class})


def related_field_factory(model_class, queryset=None):
    """
    Returns a subclass of `RelatedField` for each model_class in the registry
    """
    if queryset is None:
        queryset = model_class.objects.all()
    related_field_class = serializers.PrimaryKeyRelatedField
    kwargs = {'queryset': queryset}
    if DRF_SETTINGS['HYPERLINK_FIELDS']:
        related_field_class = serializers.HyperlinkedRelatedField
        kwargs['view_name'] = f'{label(model_class)}-detail'
    elif DRF_SETTINGS['EXPAND_FIELDS']:
        related_field_class = ExpandRelatedField
    field = type(f'{model_class.__name__}RelatedField', (related_field_class,), {})
    return field(**kwargs)


def registry_factory(factory):
    """
    Returns a mapping of the registry's model_class applied with the factory function
    """
    return {model_class: factory(model_class) for model_class in registry}


def get_grf():
    """
    Get a new `GenericRelatedField` instance for each use of the related field
    """
    return GenericRelatedField(registry_factory(related_field_factory), read_only=True)


registered_serializers = registry_factory(serializer_factory)


class ActionSerializer(DEFAULT_SERIALIZER):
    """
    Serializer for actstream.Action models in the activity feeds
    """
    actor = get_grf()
    target = get_grf()
    action_object = get_grf()

    class Meta:
        model = Action
        fields = 'id verb public description timestamp actor target action_object'.split()


class SendActionSerializer(serializers.Serializer):
    """
    Serializer used when POSTing a new action to DRF
    """
    verb = serializers.CharField(required=True, help_text='Action verb')
    target_content_type_id = serializers.CharField()
    target_object_id = serializers.CharField()
    action_object_content_type_id = serializers.CharField()
    action_object_object_id = serializers.CharField()
    description = serializers.CharField()
    public = serializers.BooleanField()


class FollowSerializer(DEFAULT_SERIALIZER):
    """
    Serializer for actstream.Follow models in the activity feeds
    """
    user = get_grf()
    follow_object = get_grf()

    class Meta:
        model = Follow
        fields = 'id flag user follow_object started actor_only'.split()


class FollowingSerializer(DEFAULT_SERIALIZER):
    """
    Serializer for actstream.Follow models in the "following" activity feeds
    """
    follow_object = get_grf()

    class Meta:
        model = Follow
        fields = ['follow_object']
