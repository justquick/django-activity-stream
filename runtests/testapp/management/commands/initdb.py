from django.core.management.base import BaseCommand
from django.core.management import call_command

from actstream.tests.base import DataTestCase
from actstream.tests.test_gfk import GFKManagerTestCase
from actstream.tests.test_zombies import ZombieTest

from testapp.models import MyUser


class Command(BaseCommand):
    help = 'Loads test actions for development'

    def handle(self, *args, **kwargs):
        if MyUser.objects.count():
            print('Already loaded')
            exit()

        call_command('createsuperuser')

        for testcase in (DataTestCase, GFKManagerTestCase, ZombieTest):
            testcase().setUp()
