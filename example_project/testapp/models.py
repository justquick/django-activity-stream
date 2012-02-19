from django.db import models
from django.contrib.comments.signals import comment_was_posted

from actstream import action

def comment_action(sender, comment=None, target=None, **kwargs):
    if comment.user:
        action.send(comment.user, verb=u'commented', action_object=comment, 
            target=comment.content_object)
comment_was_posted.connect(comment_action)

class Player(models.Model):
    state = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '#%d' % self.pk