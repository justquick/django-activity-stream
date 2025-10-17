from django.db import models
from actstream.models import AbstractAction, AbstractFollow


class CustomAction(AbstractAction):
    quest = models.CharField(max_length=200)


class CustomFollow(AbstractFollow):
    is_special = models.BooleanField(default=False)
