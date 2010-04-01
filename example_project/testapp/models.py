from django.db import models


class Player(models.Model):
    state = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '#%d' % self.pk