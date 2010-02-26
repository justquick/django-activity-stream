from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from django.contrib.syndication.views import Feed
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from actstream.models import actor_stream, model_stream, user_stream

class ObjectActivityFeed(Feed):
    def get_object(self, request, content_type_id, object_id):
        return get_object_or_404(ContentType, pk=content_type_id)\
            .get_object_for_this_type(pk=object_id)

    def title(self, obj):
        return 'Activity feed from %s' % obj

    def link(self, obj):
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return reverse('actstream_actor', None,
                    (ContentType.objects.get_for_model(obj).pk, obj.pk))
        
    def description(self, obj):
        return 'Public activities of %s' % obj
    
    def items(self, obj):
        return actor_stream(obj)[:30]
        
class AtomObjectActivityFeed(ObjectActivityFeed):
    feed_type = Atom1Feed
    subtitle = ObjectActivityFeed.description        
        
class UserActivityFeed(Feed):
    def get_object(self, request):
        return request.user

    def title(self, user):
        return 'Activity feed for your followed actors'

    def link(self, user):
        if hasattr(user, 'get_absolute_url'):
            return user.get_absolute_url()
        raise Http404
        
    def description(self, user):
        return 'Public activities of actors you follow'
    
    def items(self, user):
        return user_stream(user)[:30]
        
class AtomUserActivityFeed(UserActivityFeed):
    feed_type = Atom1Feed
    subtitle = UserActivityFeed.description
    
