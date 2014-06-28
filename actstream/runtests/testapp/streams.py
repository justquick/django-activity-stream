from datetime import datetime

from actstream.managers import ActionManager, stream


class MyActionManager(ActionManager):

    @stream
    def testfoo(self, obj, time=None):
        if time is None:
            time = datetime.now()
        return obj.actor_actions.filter(timestamp__lte=time)

    @stream
    def testbar(self, verb):
        return {'verb': verb}
