import json

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed, rfc3339_date
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed, add_domain
from django.contrib.sites.models import Site
from django.utils.encoding import force_text
from django.utils.six import text_type
from django.utils import datetime_safe
from django.views.generic import View
from django.http import HttpResponse

from actstream.models import Action, model_stream, user_stream, any_stream


class AbstractActivityStream(object):
    """
    Abstract base class for generic stream rendering.
    Supports hooks for fetching streams and formatting actions.
    """
    def get_stream(self, *args, **kwargs):
        raise NotImplementedError

    def get_object(self, *args, **kwargs):
        raise NotImplementedError

    def items(self, *args, **kwargs):
        return self.get_stream()(self.get_object(*args, **kwargs))

    def get_uri(self, action, obj=None, date=None):
        if date is None:
            date = action.timestamp
        date = datetime_safe.new_datetime(date).strftime('%Y-%m-%d')
        return 'tag:%s,%s:%s' % (Site.objects.get_current().domain, date,
                                 self.get_url(action, obj, False))

    def get_url(self, action, obj=None, domain=True):
        if not obj:
            url = reverse('actstream_detail', None, (action.pk,))
        elif hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
        else:
            ctype = ContentType.objects.get_for_model(obj)
            url = reverse('actstream_actor', None, (ctype.pk, obj.pk))
        if domain:
            return add_domain(Site.objects.get_current().domain, url)
        return url

    def format(self, action):
        item = {
            'id': self.get_uri(action),
            'url': self.get_url(action),
            'verb': action.verb,
            'published': rfc3339_date(action.timestamp),
            'actor': self.format_actor(action)
        }
        if action.description:
            item['content'] = action.description
        if action.target:
            item['target'] = self.format_target(action)
        if action.action_object:
            item['object'] = self.format_action_object(action)
        return item

    def format_item(self, action, item_type='actor'):
        obj = getattr(action, item_type)
        return {
            'id': self.get_uri(action, obj),
            'url': self.get_url(action, obj),
            'objectType': ContentType.objects.get_for_model(obj).name,
            'displayName': text_type(obj)
        }

    def format_actor(self, action):
        return self.format_item(action)

    def format_target(self, action):
        return self.format_item(action, 'target')

    def format_action_object(self, action):
        return self.format_item(action, 'action_object')


class ActivityStreamsAtomFeed(Atom1Feed):
    """
    Feed rendering class for the v1.0 Atom Activity Stream Spec
    """
    def root_attributes(self):
        attrs = super(ActivityStreamsAtomFeed, self).root_attributes()
        attrs['xmlns:activity'] = 'http://activitystrea.ms/spec/1.0/'
        return attrs

    def add_root_elements(self, handler):
        super(ActivityStreamsAtomFeed, self).add_root_elements(handler)

    def quick_elem(self, handler, key, value):
        if key == 'link':
            handler.addQuickElement(key, None, {
                'href': value, 'type': 'text/html', 'rel': 'alternate'})
        else:
            handler.addQuickElement(key, value)

    def item_quick_handler(self, handler, name, item):
        handler.startElement(name, {})
        for key, value in item.items():
            self.quick_elem(handler, key, value)
        handler.endElement(name)

    def add_item_elements(self, handler, item):
        item.pop('unique_id')
        actor = item.pop('actor')
        target = item.pop('target', None)
        action_object = item.pop('action_object', None)
        content = item.pop('content', None)

        if content:
            handler.addQuickElement('content', content, {'type': 'html'})

        for key, value in item.items():
            if value:
                self.quick_elem(handler, key, value)

        self.item_quick_handler(handler, 'author', actor)

        if action_object:
            self.item_quick_handler(handler, 'activity:object', action_object)

        if target:
            self.item_quick_handler(handler, 'activity:target', target)


class ActivityStreamsBaseFeed(AbstractActivityStream, Feed):

    def feed_extra_kwargs(self, obj):
        """
        Returns an extra keyword arguments dictionary that is used when
        initializing the feed generator.
        """
        return {}

    def item_extra_kwargs(self, action):
        """
        Returns an extra keyword arguments dictionary that is used with
        the `add_item` call of the feed generator.
        Add the 'content' field of the 'Entry' item, to be used by the custom
        feed generator.
        """
        item = self.format(action)
        item['uri'] = item.pop('url')
        item['activity:verb'] = item.pop('verb')
        return item

    def format_item(self, action, item_type='actor'):
        name = item_type == 'actor' and 'name' or 'title'
        item = super(ActivityStreamsBaseFeed, self).format_item(action, item_type)
        item[name] = item.pop('displayName')
        item['activity:object-type'] = item.pop('objectType')
        item.pop('url')
        return item

    def item_link(self, action):
        return self.get_url(action)

    def item_description(self, action):
        if action.description:
            return force_text(action.description)

    def items(self, obj):
        return self.get_stream()(obj)[:30]


class JSONActivityFeed(AbstractActivityStream, View):
    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(self.serialize(request, *args, **kwargs),
                            content_type='application/json')

    def serialize(self, request, *args, **kwargs):
        items = self.items(request, *args, **kwargs)
        return json.dumps({
            'totalItems': len(items),
            'items': [self.format(action) for action in items]
        }, indent=4 if 'pretty' in request.REQUEST else None)


class ModelActivityMixin(object):

    def get_object(self, request, content_type_id):
        return get_object_or_404(ContentType, pk=content_type_id).model_class()

    def get_stream(self):
        return model_stream


class ObjectActivityMixin(object):

    def get_object(self, request, content_type_id, object_id):
        obj = get_object_or_404(ContentType, pk=content_type_id)
        return obj.get_object_for_this_type(pk=object_id)

    def get_stream(self):
        return any_stream


class UserActivityMixin(object):

    def get_object(self, request):
        if request.user.is_authenticated():
            return request.user

    def get_stream(self):
        return user_stream


class CustomStreamMixin(object):
    name = None

    def get_object(self):
        return

    def get_stream(self):
        return getattr(Action.objects, self.name)

    def items(self, *args, **kwargs):
        return self.get_stream()(*args[1:], **kwargs)


class ModelActivityFeed(ModelActivityMixin, ActivityStreamsBaseFeed):

    def title(self, model):
        return 'Activity feed from %s' % model.__name__

    def link(self, model):
        ctype = ContentType.objects.get_for_model(model)
        return reverse('actstream_model', None, (ctype.pk,))

    def description(self, model):
        return 'Public activities of %s' % model.__name__


class ObjectActivityFeed(ObjectActivityMixin, ActivityStreamsBaseFeed):
    """
    Feed of Activity for a given object (where the object is the Object or
    Target).
    """
    def title(self, obj):
        return 'Activity for %s' % obj

    def link(self, obj):
        return self.get_url(obj)

    def description(self, obj):
        return 'Activity for %s' % obj


class UserActivityFeed(UserActivityMixin, ActivityStreamsBaseFeed):

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


class AtomModelActivityFeed(ModelActivityFeed):
    feed_type = ActivityStreamsAtomFeed
    subtitle = ModelActivityFeed.description


class AtomObjectActivityFeed(ObjectActivityFeed):
    feed_type = ActivityStreamsAtomFeed
    subtitle = ObjectActivityFeed.description


class AtomUserActivityFeed(UserActivityFeed):
    feed_type = ActivityStreamsAtomFeed
    subtitle = UserActivityFeed.description


class UserJSONActivityFeed(UserActivityMixin, JSONActivityFeed):
    pass


class ModelJSONActivityFeed(ModelActivityMixin, JSONActivityFeed):
    pass


class ObjectJSONActivityFeed(ObjectActivityMixin, JSONActivityFeed):
    pass


class CustomJSONActivityFeed(CustomStreamMixin, JSONActivityFeed):
    pass
