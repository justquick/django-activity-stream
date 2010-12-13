from django.db import models


class Player(models.Model):
    state = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '#%d' % self.pk

class Story(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __unicode__(self):
        return self.title
        
    def get_absolute_url(self):
        return "/story/%d" % self.id
