from random import choice

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection

from actstream.signals import action
from actstream.models import model_stream
from actstream.tests.base import ActivityBaseTestCase


class ZombieTest(ActivityBaseTestCase):
    human = 10
    zombie = 1

    def setUp(self):
        self.User = get_user_model()
        super(ZombieTest, self).setUp()
        settings.DEBUG = True

        player_generator = lambda n, count: [self.User.objects.create(
            username='%s%d' % (n, i)) for i in range(count)]

        self.humans = player_generator('human', self.human)
        self.zombies = player_generator('zombie', self.zombie)

        self.zombie_apocalypse()

    def tearDown(self):
        settings.DEBUG = False
        super(ZombieTest, self).tearDown()

    def zombie_apocalypse(self):
        humans = self.humans[:]
        zombies = self.zombies[:]
        while humans:
            for z in self.zombies:
                victim = choice(humans)
                humans.remove(victim)
                zombies.append(victim)
                action.send(z, verb='killed', target=victim)
                if not humans:
                    break

    def check_query_count(self, queryset):
        ci = len(connection.queries)

        result = list([map(str, (x.actor, x.target, x.action_object))
                       for x in queryset])
        self.assertTrue(len(connection.queries) - ci <= 4,
                        'Too many queries, got %d expected no more than 4' %
                        len(connection.queries))
        return result

    def test_query_count(self):
        queryset = model_stream(self.User)
        result = self.check_query_count(queryset)
        self.assertEqual(len(result), 10)

    def test_query_count_sliced(self):
        queryset = model_stream(self.User)[:5]
        result = self.check_query_count(queryset)
        self.assertEqual(len(result), 5)
