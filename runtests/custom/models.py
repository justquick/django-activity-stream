from actstream.models import AbstractAction, AbstractFollow
from django.db import models

class CustomAction(AbstractAction):
    quest = models.CharField(max_length=200)


class CustomFollow(AbstractFollow):
    is_special = models.BooleanField(default=False)
