import json

from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed, rfc3339_date
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.views import Feed, add_domain
from django.contrib.sites.models import Site
from django.utils.encoding import force_str
from django.utils import datetime_safe
from django.views.generic import View
from django.http import HttpResponse, Http404
from django.urls import reverse

from actstream.models import Action, model_stream, user_stream, any_stream


class AbstractActivityStream:
    """
    Abstract base class for all stream rendering.
    Supports hooks for fetching streams and formatting actions.
    """
    def get_stream(self, *args, **kwargs):
        """
        Returns a stream method to use.
        """
        raise NotImplementedError   

    def get_object(self, *args, **kwargs):
        """
        Returns the object (eg user or actor) that the stream is for.
        """
        raise NotImplementedError

    def items(self, *args, **kwargs):
        """
        Returns a queryset of Actions to use based on the stream method and object.
        """
        return self.get_stream()(self.get_object(*args, **kwargs))

    def get_uri(self, action, obj=None, date=None):
        """
        Returns an RFC3987 IRI ID for the given object, action and date.
        """
        if date is None:
            date = action.timestamp
        date = datetime_safe.new_datetime(date).strftime('%Y-%m-%d')
        return 'tag:{},{}:{}'.format(Site.objects.get_current().domain, date,
                                 self.get_url(action, obj, False))

    def get_url(self, action, obj=None, domain=True):
        """
        Returns an RFC3987 IRI for a HTML representation of the given object, action.
        If domain is true, the current site's domain will be added.
        """
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
        """
        Returns a formatted dictionary for the given action.
        """
        item = {
            'id': self.get_uri(action),
            'url': self.get_url(action),
            'verb': action.verb,
            'published': rfc3339_date(action.timestamp),
            'actor': self.format_actor(action),
            'title': str(action),
        }
        if action.description:
            item['content'] = action.description
        if action.target:
            item['target'] = self.format_target(action)
        if action.action_object:
            item['object'] = self.format_action_object(action)
        return item

    def format_item(self, action, item_type='actor'):
        """
        Returns a formatted dictionary for an individual item based on the action and item_type.
        """
        obj = getattr(action, item_type)
        return {
            'id': self.get_uri(action, obj),
            'url': self.get_url(action, obj),
            'objectType': ContentType.objects.get_for_model(obj).name,
            'displayName': str(obj)
        }

    def format_actor(self, action):
        """
        Returns a formatted dictionary for the actor of the action.
        """
        return self.format_item(action)

    def format_target(self, action):
        """
        Returns a formatted dictionary for the target of the action.
        """
        return self.format_item(action, 'target')

    def format_action_object(self, action):
        """
        Returns a formatted dictionary for the action object of the action.
        """
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
        item.pop('title', None)
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
            return force_str(action.description)

    def items(self, obj):
        return self.get_stream()(obj)[:30]


class JSONActivityFeed(AbstractActivityStream, View):
    """
    Feed that generates feeds compatible with the v1.0 JSON Activity Stream spec
    """
    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(self.serialize(request, *args, **kwargs),
                            content_type='application/json')

    def serialize(self, request, *args, **kwargs):
        items = self.items(request, *args, **kwargs)
        return json.dumps({
            'totalItems': len(items),
            'items': [self.format(action) for action in items]
        }, indent=4 if 'pretty' in request.GET or 'pretty' in request.POST else None)


class ModelActivityMixin:

    def get_object(self, request, content_type_id):
        return get_object_or_404(ContentType, pk=content_type_id).model_class()

    def get_stream(self):
        return model_stream


class ObjectActivityMixin:

    def get_object(self, request, content_type_id, object_id):
        ct = get_object_or_404(ContentType, pk=content_type_id)
        try:
            obj = ct.get_object_for_this_type(pk=object_id)
        except ObjectDoesNotExist:
            raise Http404('No %s matches the given query.' % ct.model_class()._meta.object_name)
        return obj

    def get_stream(self):
        return any_stream

class StreamKwargsMixin:
        
    def items(self, request, *args, **kwargs):
        return self.get_stream()(self.get_object(request, *args, **kwargs),**self.get_stream_kwargs(request))
    

class UserActivityMixin:

    def get_object(self, request):
        if request.user.is_authenticated:
            return request.user

    def get_stream(self):
        return user_stream

    def get_stream_kwargs(self, request):
        stream_kwargs = {}
        if 'with_user_activity' in request.GET:
            stream_kwargs['with_user_activity'] = request.GET['with_user_activity'].lower() == 'true'
        return stream_kwargs

class CustomStreamMixin:
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


class AtomUserActivityFeed(UserActivityFeed):
    """
    Atom feed of Activity for a given user (where actions are those that the given user follows).
    """
    feed_type = ActivityStreamsAtomFeed
    subtitle = UserActivityFeed.description


class AtomModelActivityFeed(ModelActivityFeed):
    """
    Atom feed of Activity for a given model (where actions involve the given model as any of the entities).
    """
    feed_type = ActivityStreamsAtomFeed
    subtitle = ModelActivityFeed.description


class AtomObjectActivityFeed(ObjectActivityFeed):
    """
    Atom feed of Activity for a given object (where actions involve the given object as any of the entities).
    """
    feed_type = ActivityStreamsAtomFeed
    subtitle = ObjectActivityFeed.description


class UserJSONActivityFeed(UserActivityMixin, StreamKwargsMixin, JSONActivityFeed):
    """
    JSON feed of Activity for a given user (where actions are those that the given user follows).
    """
    pass


class ModelJSONActivityFeed(ModelActivityMixin, JSONActivityFeed):
    """
    JSON feed of Activity for a given model (where actions involve the given model as any of the entities).
    """
    pass


class ObjectJSONActivityFeed(ObjectActivityMixin, JSONActivityFeed):
    """
    JSON feed of Activity for a given object (where actions involve the given object as any of the entities).
    """
    pass


class CustomJSONActivityFeed(CustomStreamMixin, JSONActivityFeed):
    """
    JSON feed of Activity for a custom stream. self.name should be the name of the custom stream as defined in the Manager
    and arguments may be passed either in the url or when calling as_view(...)
    """
    pass
