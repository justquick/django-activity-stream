from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed, rfc3339_date, get_tag_uri
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from xml.sax import handler

try:
    from django.contrib.syndication.views import Feed
except ImportError: # Pre 1.2
    from django.contrib.syndication.feeds import Feed

from actstream.models import actor_stream, model_stream, user_stream, object_stream

class ObjectActivityFeed(Feed):
    """
    Feed of Activity for a given object (where the object is the Object or Target)
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
        i = object_stream(obj)
        if i:
            return i[:30]
        return []
        
class AtomObjectActivityFeed(ObjectActivityFeed):
    feed_type = Atom1Feed
    subtitle = ObjectActivityFeed.description

class ActivityStreamsGenerator(Atom1Feed):
    """
    Custom feed generator for Activity Stream feeds
    """
    def root_attributes(self):
        attrs = super(ActivityStreamsGenerator, self).root_attributes()
        attrs['xmlns:activity'] = 'http://activitystrea.ms/spec/1.0/'
        return attrs

    def add_root_elements(self, handler):
        super(ActivityStreamsGenerator, self).add_root_elements(handler)
        # handler.addQuickElement('itunes:explicit', 'clean')
        
    def add_item_elements(self, handler, item):
        super(ActivityStreamsGenerator, self).add_item_elements(handler, item)
        print item
        # <activity:verb>post</activity:verb>
        handler.addQuickElement(u"activity:verb", item['verb'])

        if 'actor' in item:
#        <author>
            handler.startElement('author', {})
#           <name>Geraldine</name>
            handler.addQuickElement('name', item['actor'].display_name)
#           <uri>http://example.com/geraldine</uri>
            handler.addQuickElement('uri', get_tag_uri(item['actor'].get_absolute_url(), None))
#           <id>tag:photopanic.example.com,2009:person/4859</id>
            handler.addQuickElement('id', item['actor'].get_absolute_url())
#           <activity:object-type>person</activity:object-type>
            handler.addQuickElement('activity:object-type', 'person')
#           <link rel="alternate" type="text/html" href="http://example.com/geraldine" />
            handler.addQuickElement('link', get_tag_uri(item['actor'].get_absolute_url(), None), {'type':'text/html'})
            handler.endElement('author')
#        </author>


        if 'object' in item:
#       <activity:object>
            handler.startElement('activity:object', {})
#           <id>tag:photopanic.example.com,2009:photo/4352</id>
            handler.addQuickElement('id', item['object_id'])
#           <title>My Cat</title>
            handler.addQuickElement('title', item['object_title'])
#           <published>2009-11-02T15:29:00Z</published>
            handler.addQuickElement(
                u"published", rfc3339_date(item['object_timestamp']).decode('utf-8'))

#           <link rel="alternate" type="text/html" href="http://example.com/geraldine/photos/4352" />
            handler.addQuickElement('link', item['object'].get_absolute_url(), {'type':'text/html'})
#           <activity:object-type>photo</activity:object-type>
            handler.addQuickElement('activity:object-type', item['object_object_type'])
#       </activity:object>
            handler.endElement('activity:object')

        if 'target' in item:
#        <activity:target>
            handler.startElement('activity:target', {})
#          <id>tag:photopanic.example.com,2009:photo-album/2519</id>
            handler.addQuickElement('id', item['target_id'])
#          <title>My Pets</title>
            handler.addQuickElement('title', item['target_title'])
#          <link rel="alternate" type="text/html" href="/geraldine/albums/pets" />
#          <activity:object-type>photo-album</activity:object-type>
            handler.addQuickElement('activity:object-type', str(item['target_object_type']))
#        </activity:target>
            handler.endElement('activity:target')


class ActivityStreamsObjectActivityFeed(AtomObjectActivityFeed):

    feed_type = ActivityStreamsGenerator

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
        Add the 'content' field of the 'Entry' item, to be used by the custom feed generator.
        """
        print vars(obj)
#        {
#            'actor_content_type_id': 21L,
#            'description': None,
#            'timestamp': datetime.datetime(2011, 8, 18, 23, 16, 9),
#            '_state': '<django.db.models.base.ModelState object at 0x1057357d0>',
#            '_target_cache': None,
#            'public': True,
#            '_actor_cache': '<Person: Steve>',
#            'actor_object_id': 1L,
#            'verb': u'updated',
#            'verb_uri_prefix': 'http://activitystrea.ms/schema/1.0/',
#            'target_object_id': None,
#            'action_object_content_type_id': 32L,
#            'target_content_type_id': None,
#            'id': 64L,
#            'action_object_object_id': 1L
#        }
        try:
            object_id = obj.action_object.get_absolute_url()
        except Exception, e:
            object_id = obj.action_object_content_type.model + "/" + str(obj.action_object.id)

        object_id = get_tag_uri(object_id, None)

        item =  {
            'actor': obj.actor,
            'verb': obj.verb_uri_prefix + obj.verb,
            # action object
            'object_timestamp': obj.timestamp,
            'object': obj.action_object,
            'object_id': object_id,
            'object_title': obj.action_object.__unicode__(),
            'object_object_type': obj.action_object_content_type.model,
        }

        if obj.target:
            try:
                target_id = obj.target.get_absolute_url()
            except Exception, e:
                target_id = obj.target_content_type.model + "/" + str(obj.action_object.id)

            target_id = get_tag_uri(target_id, obj.timestamp)

            item['target'] = obj.target
            item['target_id'] = target_id
            item['target_title'] = obj.target.__unicode__()
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
    
