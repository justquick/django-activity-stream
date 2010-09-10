from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
try:
    from django.contrib.syndication.views import Feed
except ImportError: # Pre 1.2
    from django.contrib.syndication.feeds import Feed

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
        i = actor_stream(obj)
        if i:
            return i[:30]
        return []
        
class AtomObjectActivityFeed(ObjectActivityFeed):
    feed_type = Atom1Feed
    subtitle = ObjectActivityFeed.description        
        
class ModelActivityFeed(Feed):
    def get_object(self, request, content_type_id):
        return get_object_or_404(ContentType, pk=content_type_id).model_class()

    def title(self, model):
        return 'Activity feed from %s' % model

    def link(self, model):
        return reverse('actstream_model', None, (ContentType.objects.get_for_model(model).pk,))
        
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
    
