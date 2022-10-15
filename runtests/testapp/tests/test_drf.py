from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.urls import reverse

from actstream.tests.test_drf import BaseDRFTestCase
from actstream.drf.serializers import registered_serializers as serializers
from testapp.models import MyUser, Player
from testapp_nested.models.my_model import NestedModel
from testapp.drf import GroupSerializer


class DRFTestAppTests(BaseDRFTestCase):

    def test_urls(self):
        self._check_urls('actions', 'follows', 'groups', 'sites',
                         'players', 'nested-models', 'my-users')

    def test_serializers(self):

        models = (Group, MyUser, Player, Site, NestedModel)
        self.assertSetEqual(serializers.keys(), models, domap=False)

        groups = self.get(reverse('group-list'))
        assert len(groups) == 2
        self.assertSetEqual(GroupSerializer.Meta.fields, groups[0].keys())
