from django.contrib.syndication.views import Feed
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from util import actor_stream, model_stream, user_stream

class UserActivityFeed(Feed):
    def get_object(self, request, username):
        return get_object_or_404(User, username=username)

    def title(self, user):
        return 'Activity feed from user: %s' % user

    def link(self, user):
        return user.get_absolute_url()
        
    def description(self, user):
        return 'Public activities of user: %s' % user
    
    def items(self, user):
        return actor_stream(user)[:30]
        
class ActorActivityFeed(Feed):
    def get_object(self, request):
        return request.user

    def title(self, user):
        return 'Activity feed for your followed actors'

    def link(self, user):
        return user.get_absolute_url()
        
    def description(self, user):
        return 'Public activities of actors you follow'
    
    def items(self, user):
        return user_stream(user)[:30]