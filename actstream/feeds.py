from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed, rfc3339_date, get_tag_uri
from django.contrib.contenttypes.models import ContentType

try:
    from django.contrib.syndication.views import Feed
except ImportError:   # Pre 1.2
    from django.contrib.syndication.feeds import Feed

from actstream.models import model_stream, user_stream, action_object_stream


class AtomWithContentFeed(Atom1Feed):

    def add_item_elements(self, handler, item):
        super(AtomWithContentFeed, self).add_item_elements(handler, item)
        if 'content' in item:
            handler.addQuickElement(u"content", item['content'],
                {'type': 'html'})


class ObjectActivityFeed(Feed):
    """
    Feed of Activity for a given object (where the object is the Object or
    Target).
    """

    def get_object(self, request, content_type_id, object_id):
        return get_object_or_404(ContentType, pk=content_type_id)\
            .get_object_for_this_type(pk=object_id)

    def title(self, obj):
        return 'Activity for %s' % obj

    def link(self, obj):
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return reverse('actstream_actor', None,
                    (ContentType.objects.get_for_model(obj).pk, obj.pk))

    def description(self, obj):
        return 'Activity for %s' % obj

    def items(self, obj):
        i = action_object_stream(obj)
        if i:
            return i[:30]
        return []

    def item_extra_kwargs(self, obj):
        return  {
            'content': obj.description,
        }


class AtomObjectActivityFeed(ObjectActivityFeed):
    feed_type = AtomWithContentFeed
    subtitle = ObjectActivityFeed.description


class ActivityStreamsFeed(AtomWithContentFeed):
    """
    Custom feed generator for Activity Stream feeds
    """

    def root_attributes(self):
        attrs = super(ActivityStreamsFeed, self).root_attributes()
        attrs['xmlns: activity'] = 'http: //activitystrea.ms/spec/1.0/'
        return attrs

    def add_root_elements(self, handler):
        super(ActivityStreamsFeed, self).add_root_elements(handler)

    def add_item_elements(self, handler, item):
        super(ActivityStreamsFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u"activity: verb", item['verb'])

        if 'actor' in item:
            handler.startElement('author', {})
            handler.addQuickElement('name', item['actor'].display_name)
            handler.addQuickElement('uri', get_tag_uri(
                item['actor'].get_absolute_url(), None))
            handler.addQuickElement('id', item['actor'].get_absolute_url())
            handler.addQuickElement('activity: object-type', 'person')
            handler.addQuickElement('link', get_tag_uri(
                item['actor'].get_absolute_url(), None), {'type': 'text/html'})
            handler.endElement('author')

        if 'object' in item:
            handler.startElement('activity: object', {})
            handler.addQuickElement('id', item['object_id'])
            handler.addQuickElement('title', item['object_title'])
            handler.addQuickElement('published',
                rfc3339_date(item['object_timestamp']).decode('utf-8'))
            handler.addQuickElement('link', item['object'].get_absolute_url(),
                {'type': 'text/html'})
            handler.addQuickElement('activity: object-type',
                item['object_object_type'])
            handler.endElement('activity: object')

        if 'target' in item:
            handler.startElement('activity: target', {})
            handler.addQuickElement('id', item['target_id'])
            handler.addQuickElement('title', item['target_title'])
            handler.addQuickElement('activity: object-type',
                str(item['target_object_type']))
            handler.endElement('activity: target')


class ActivityStreamsObjectActivityFeed(AtomObjectActivityFeed):
    feed_type = ActivityStreamsFeed

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
        try:
            object_id = obj.action_object.get_absolute_url()
        except:
            object_id = '%s/%s' % (obj.action_object_content_type.model,
                obj.action_object.id)

        object_id = get_tag_uri(object_id, None)

        item = {
            'content': obj.description,
            'actor': obj.actor,
            'verb': obj.verb_uri_prefix + obj.verb,
            # action object
            'object_timestamp': obj.timestamp,
            'object': obj.action_object,
            'object_id': object_id,
            'object_title': unicode(obj.action_object),
            'object_object_type': obj.action_object_content_type.model,
        }

        if obj.target:
            try:
                target_id = obj.target.get_absolute_url()
            except Exception:
                target_id = '%s/%s' % (obj.target_content_type.model,
                    obj.action_object.id)

            target_id = get_tag_uri(target_id, obj.timestamp)

            item['target'] = obj.target
            item['target_id'] = target_id
            item['target_title'] = unicode(obj.target)
            item['target_object_type'] = obj.target_content_type.name

        return item


class ModelActivityFeed(Feed):

    def get_object(self, request, content_type_id):
        return get_object_or_404(ContentType, pk=content_type_id).model_class()

    def title(self, model):
        return 'Activity feed from %s' % model

    def link(self, model):
        return reverse('actstream_model', None,
                (ContentType.objects.get_for_model(model).pk,))

    def description(self, model):
        return 'Public activities of %s' % model

    def items(self, model):
        i = model_stream(model)
        if i:
            return i[:30]
        return []


class AtomModelActivityFeed(ModelActivityFeed):
    feed_type = Atom1Feed
    subtitle = ModelActivityFeed.description


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
        return reverse('actstream_actor', None,
            (ContentType.objects.get_for_model(user).pk, user.pk))

    def description(self, user):
        return 'Public activities of actors you follow'

    def items(self, user):
        i = user_stream(user)
        if i:
            return i[:30]
        return []


class AtomUserActivityFeed(UserActivityFeed):
    feed_type = Atom1Feed
    subtitle = UserActivityFeed.description
