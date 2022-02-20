from django.core.management.base import BaseCommand

from actstream.tests.base import DataTestCase
from actstream.tests.test_gfk import GFKManagerTestCase
from actstream.tests.test_zombies import ZombieTest
from actstream.registry import registry


class Command(BaseCommand):
    help = 'Loads test actions for development'

    def handle(self, *args, **kwargs):
        for testcase in (DataTestCase, GFKManagerTestCase, ZombieTest):
            testcase().setUp()
