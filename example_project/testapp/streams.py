from datetime import datetime

from django.contrib.contenttypes.models import ContentType

from actstream.managers import ActionManager, stream


class MyActionManager(ActionManager):

    @stream
    def testfoo(self, object, time=None):
        if time is None:
            time = datetime.now()
        return object.actor_actions.filter(timestamp__lte = time)
