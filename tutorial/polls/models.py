import datetime

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User

from django_comments.models import Comment
from django_comments.signals import comment_was_posted

from actstream import action
from actstream.registry import register
from actstream.managers import ActionManager, stream


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.choice_text


class QuestionActionManager(ActionManager):
    @stream
    def with_votes(self):
        return {'votes__gt': 0}


register(Question, Choice, User, Comment)


@receiver(comment_was_posted)
def commented_question_handler(sender, **kwargs):
    comment = kwargs['comment']
    request = kwargs['request']
    if request.user.is_authenticated():
        action.send(request.user, verb='commented', action_object=comment, target=comment.content_object)
