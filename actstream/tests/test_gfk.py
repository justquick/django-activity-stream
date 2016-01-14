from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group

from actstream.models import Action
from actstream.compat import get_user_model
from actstream.tests.base import LTE


class GFKManagerTestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user_ct = ContentType.objects.get_for_model(User)
        self.group_ct = ContentType.objects.get_for_model(Group)
        self.group, _ = Group.objects.get_or_create(name='CoolGroup')
        self.user1, _ = User.objects.get_or_create(username='admin')
        self.user2, _ = User.objects.get_or_create(username='Two')
        self.user3, _ = User.objects.get_or_create(username='Three')
        self.user4, _ = User.objects.get_or_create(username='Four')
        Action.objects.get_or_create(
            actor_content_type=self.user_ct,
            actor_object_id=self.user1.id,
            verb='followed',
            target_content_type=self.user_ct,
            target_object_id=self.user2.id
        )
        Action.objects.get_or_create(
            actor_content_type=self.user_ct,
            actor_object_id=self.user1.id,
            verb='followed',
            target_content_type=self.user_ct,
            target_object_id=self.user3.id
        )
        Action.objects.get_or_create(
            actor_content_type=self.user_ct,
            actor_object_id=self.user1.id,
            verb='followed',
            target_content_type=self.user_ct,
            target_object_id=self.user4.id
        )
        Action.objects.get_or_create(
            actor_content_type=self.user_ct,
            actor_object_id=self.user1.id,
            verb='joined',
            target_content_type=self.group_ct,
            target_object_id=self.group.id
        )

    def test_fetch_generic_relations(self):
        # baseline without fetch_generic_relations
        _actions = Action.objects.filter(actor_content_type=self.user_ct,
                                         actor_object_id=self.user1.id)
        actions = lambda: _actions._clone()
        num_content_types = len(set(actions().values_list(
            'target_content_type_id', flat=True)))
        n = actions().count()

        # compare to fetching only 1 generic relation
        full, generic = actions(), actions().fetch_generic_relations('target')
        self.assertNumQueries(LTE(n + 1),
                              lambda: [a.target for a in full])
        self.assertNumQueries(LTE(num_content_types + 2),
                              lambda: [a.target for a in generic])

        action_targets = [(a.id, a.target) for a in actions()]
        action_targets_fetch_generic = [
            (a.id, a.target)
            for a in actions().fetch_generic_relations('target')]
        self.assertEqual(action_targets, action_targets_fetch_generic)

        # compare to fetching all generic relations
        num_content_types = len(set(sum(actions().values_list(
            'actor_content_type_id', 'target_content_type_id'), ())))
        full, generic = actions(), actions().fetch_generic_relations()
        self.assertNumQueries(LTE(2 * n + 1),
                              lambda: [(a.actor, a.target) for a in full])
        self.assertNumQueries(LTE(num_content_types + 2),
                              lambda: [(a.actor, a.target) for a in generic])

        action_actor_targets = [(a.id, a.actor, a.target) for a in actions()]
        action_actor_targets_fetch_generic_all = [
            (a.id, a.actor, a.target)
            for a in actions().fetch_generic_relations()]
        self.assertEqual(action_actor_targets,
                         action_actor_targets_fetch_generic_all)

        # fetch only 1 generic relation, but access both gfks
        generic = lambda: actions().fetch_generic_relations('target')
        self.assertNumQueries(LTE(n + num_content_types + 2), lambda: [
            (a.actor, a.target) for a in generic()])
        action_actor_targets_fetch_generic_target = [
            (a.id, a.actor, a.target) for a in generic()]
        self.assertEqual(action_actor_targets,
                         action_actor_targets_fetch_generic_target)
