from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed, rfc3339_date
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import Site
from django.utils.six import text_type
from django.utils import datetime_safe

from actstream.models import model_stream, user_stream, target_stream, action_object_stream


def get_tag_uri(obj, date):
    date = datetime_safe.new_datetime(date).strftime('%Y-%m-%d')
    return 'tag:%s,%s:%s' % (Site.objects.get_current().domain, date, get_url(obj))


def get_url(obj):
    if not obj:
        return 'None'
    if hasattr(obj, 'get_absolute_url'):
        return obj.get_absolute_url()
    ctype = ContentType.objects.get_for_model(obj)
    return reverse('actstream_actor', None, (ctype.pk, obj.pk))


class ActivityStreamsAtomFeed(Atom1Feed):
    """
    Feed class for the v1.0 Atom Activity Stream Spec
    """

    def root_attributes(self):
        attrs = super(ActivityStreamsAtomFeed, self).root_attributes()
        attrs['xmlns:activity'] = 'http://activitystrea.ms/spec/1.0/'
        return attrs

    def add_root_elements(self, handler):
        super(ActivityStreamsAtomFeed, self).add_root_elements(handler)

    def add_item_elements(self, handler, item):
        super(ActivityStreamsAtomFeed, self).add_item_elements(handler, item)
        actor = item.pop('actor')
        target = item.pop('target', None)
        action_object = item.pop('action_object', None)
        content = item.pop('content', None)

        if content:
            handler.addQuickElement('content', content, {'type': 'html'})
        [handler.addQuickElement(key, value)
         for key, value in item.items() if value]

        handler.startElement('author', {})
        [handler.addQuickElement(*args) for args in actor]
        handler.endElement('author')

        if action_object:
            handler.startElement('activity:object', {})
            [handler.addQuickElement(*args) for args in action_object]
            handler.endElement('activity:object')

        if target:
            handler.startElement('activity:target', {})
            [handler.addQuickElement(*args) for args in target]
            handler.endElement('activity:target')


class ActivityStreamsBaseFeed(Feed):

    def feed_extra_kwargs(self, obj):
        """
        Returns an extra keyword arguments dictionary that is used when
        initializing the feed generator.
        """
        return {}

    def item_extra_kwargs(self, obj):
        """
        Returns an extra keyword arguments dictionary that is used with
        the `add_item` call of the feed generator.
        Add the 'content' field of the 'Entry' item, to be used by the custom
        feed generator.
        """
        item = {
            'id': text_type(obj.pk),
            'uri': get_tag_uri(obj, obj.timestamp),
            'content': obj.description,
            'activity:verb': obj.verb,
            'published': rfc3339_date(obj.timestamp),
            'actor': self.format_item_attrs(obj)
        }
        if obj.target:
            item['target'] = self.format_item_attrs(obj, 'target')
        if obj.action_object:
            item['object'] = self.format_item_attrs(obj, 'action_object')
        return item

    def format_item_attrs(self, obj, item_type='actor'):
        name = item_type == 'actor' and 'name' or 'title'
        item_obj = getattr(obj, item_type)
        return [
            (name, text_type(item_obj)),
            ('uri', get_tag_uri(item_obj, obj.timestamp)),
            ('id', text_type(item_obj.pk)),
            ('activity:object-type',
             getattr(obj, '%s_content_type' % item_type).name),
            ('link', get_url(item_obj),
             {'type': 'text/html', 'rel': 'alternate'}),
        ]


class ModelActivityFeed(Feed):

    def get_object(self, request, content_type_id):
        return get_object_or_404(ContentType, pk=content_type_id).model_class()

    def title(self, model):
        return 'Activity feed from %s' % model.__name__

    def link(self, model):
        ctype = ContentType.objects.get_for_model(model)
        return reverse('actstream_model', None, (ctype.pk,))

    def description(self, model):
        return 'Public activities of %s' % model.__name__

    def items(self, model):
        i = model_stream(model)
        return i[:30] if i else []


class AtomModelActivityFeed(ActivityStreamsBaseFeed, ModelActivityFeed):
    feed_type = ActivityStreamsAtomFeed
    subtitle = ModelActivityFeed.description


class ObjectActivityFeed(Feed):
    """
    Feed of Activity for a given object (where the object is the Object or
    Target).
    """

    def get_object(self, request, content_type_id, object_id):
        obj = get_object_or_404(ContentType, pk=content_type_id)
        return obj.get_object_for_this_type(pk=object_id)

    def title(self, obj):
        return 'Activity for %s' % obj

    def link(self, obj):
        return get_url(obj)

    def description(self, obj):
        return 'Activity for %s' % obj

    def items(self, obj):
        i = target_stream(obj) | action_object_stream(obj)
        return i[:30] if i else []

    def item_extra_kwargs(self, obj):
        return {'content': obj.description}


class AtomObjectActivityFeed(ActivityStreamsBaseFeed, ObjectActivityFeed):
    feed_type = ActivityStreamsAtomFeed
    subtitle = ObjectActivityFeed.description


class UserActivityFeed(Feed):

    def get_object(self, request):
        if request.user.is_authenticated():
            return request.user

    def title(self, user):
        return 'Activity feed for your followed actors'

    def link(self, user):
        if not user:
            return reverse('actstream')
        if hasattr(user, 'get_absolute_url'):
            return user.get_absolute_url()
        ctype = ContentType.objects.get_for_model(user)
        return reverse('actstream_actor', None, (ctype.pk, user.pk))

    def description(self, user):
        return 'Public activities of actors you follow'

    def items(self, user):
        i = user_stream(user)
        return i[:30] if i else []


class AtomUserActivityFeed(ActivityStreamsBaseFeed, UserActivityFeed):
    feed_type = ActivityStreamsAtomFeed
    subtitle = UserActivityFeed.description
