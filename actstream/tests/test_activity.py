# -*- coding: utf-8  -*-
import django
from django.contrib.auth.models import Group

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate, get_language
from django.urls import reverse

from actstream.models import (Action, Follow, model_stream, user_stream,
                              actor_stream, following, followers)
from actstream.actions import follow, unfollow
from actstream.signals import action
from actstream.tests.base import DataTestCase, render


class ActivityTestCase(DataTestCase):
    urls = 'actstream.urls'

    def test_aauser1(self):
        self.assertSetEqual(self.user1.actor_actions.all(), [
            'admin commented on CoolGroup %s ago' % self.timesince,
            'admin started following Two %s ago' % self.timesince,
            'admin joined CoolGroup %s ago' % self.timesince,
        ])

    def test_user2(self):
        self.assertSetEqual(actor_stream(self.user2), [
            'Two started following CoolGroup %s ago' % self.timesince,
            'Two joined CoolGroup %s ago' % self.timesince,
        ])

    def test_user4(self):
        self.assertSetEqual(actor_stream(self.user4), [
            'Four started blacklisting Three %s ago' % self.timesince,
            'Four started liking admin %s ago' % self.timesince,
            'Four started watching NiceGroup %s ago' % self.timesince,
            'Four started liking NiceGroup %s ago' % self.timesince,
        ])

    def test_group(self):
        self.assertSetEqual(actor_stream(self.group),
                            ['CoolGroup responded to admin: Sweet Group!... '
                             '%s ago' % self.timesince])

    def test_following(self):
        self.assertEqual(list(following(self.user1)), [self.user2])
        self.assertEqual(len(following(self.user2, self.User)), 0)

    def test_following_with_flag(self):
        self.assertCountEqual(list(following(self.user4, flag='liking')), [self.another_group, self.user1])
        self.assertEqual(list(following(self.user4, flag='watching')), [self.another_group])
        self.assertEqual(list(following(self.user4, flag='blacklisting')), [self.user3])
        self.assertEqual(list(following(self.user4, self.User, flag='liking')), [self.user1])

    def test_followers(self):
        self.assertEqual(list(followers(self.group)), [self.user2])

    def test_followers_with_flag(self):
        self.assertEqual(list(followers(self.another_group, flag='liking')), [self.user4])
        self.assertEqual(list(followers(self.another_group, flag='watching')), [self.user4])
        self.assertEqual(list(followers(self.user1, flag='liking')), [self.user4])
        self.assertEqual(list(followers(self.user3, flag='blacklisting')), [self.user4])

    def test_empty_follow_stream(self):
        unfollow(self.user1, self.user2)
        self.assertFalse(user_stream(self.user1))

        self.assertSetEqual(
            user_stream(self.user3, with_user_activity=True),
            ['Three liked actstream %s ago' % self.timesince]
        )

    def test_follow_unicode(self):
        """ Reproduce bug #201, that pops, for example, in django admin
        """
        self.user1.username = 'éé'
        self.user1.save()
        f = follow(self.user1, self.user2)
        # just to check that it do not meet a UnicodeDecodeError
        self.assertIn('éé', str(f))

    def test_stream(self):
        self.assertSetEqual(user_stream(self.user1), [
            'Two started following CoolGroup %s ago' % self.timesince,
            'Two joined CoolGroup %s ago' % self.timesince,
        ])
        self.assertSetEqual(user_stream(self.user2),
                            ['CoolGroup responded to admin: '
                             'Sweet Group!... %s ago' % self.timesince])

    def test_stream_with_flag(self):
        self.assertSetEqual(user_stream(self.user4, follow_flag='blacklisting'), [
            'Three liked actstream %s ago' % self.timesince
        ])

    def test_stream_stale_follows(self):
        """
        user_stream() should ignore Follow objects with stale actor
        references.
        """
        self.user2.delete()
        self.assertNotIn('Two', str(user_stream(self.user1)))

    def test_action_object(self):
        created = action.send(self.user1, verb='created comment',
                              action_object=self.comment, target=self.group,
                              timestamp=self.testdate)[0][1]

        self.assertEqual(created.actor, self.user1)
        self.assertEqual(created.action_object, self.comment)
        self.assertEqual(created.target, self.group)
        self.assertEqual(str(created),
                         'admin created comment admin: Sweet Group!... on '
                         'CoolGroup %s ago' % self.timesince)

    def test_doesnt_generate_duplicate_follow_records(self):
        g = Group.objects.get_or_create(name='DupGroup')[0]
        s = self.User.objects.get_or_create(username='dupuser')[0]

        f1 = follow(s, g)
        self.assertTrue(f1 is not None, "Should have received a new follow "
                                        "record")
        self.assertTrue(isinstance(f1, Follow), "Returns a Follow object")

        follows = Follow.objects.filter(user=s, object_id=g.pk,
                                        content_type=self.group_ct)
        self.assertEqual(1, follows.count(),
                         "Should only have 1 follow record here")

        f2 = follow(s, g)
        follows = Follow.objects.filter(user=s, object_id=g.pk,
                                        content_type=self.group_ct)
        self.assertEqual(1, follows.count(),
                         "Should still only have 1 follow record here")
        self.assertTrue(f2 is not None, "Should have received a Follow object")
        self.assertTrue(isinstance(f2, Follow), "Returns a Follow object")
        self.assertEqual(f1, f2, "Should have received the same Follow "
                                 "object that I first submitted")

    def test_following_models_OR_query(self):
        follow(self.user1, self.group, timestamp=self.testdate)
        self.assertSetEqual([self.user2, self.group],
                            following(self.user1, Group, self.User), domap=False)

    def test_y_no_orphaned_follows(self):
        follows = Follow.objects.count()
        self.user2.delete()
        self.assertEqual(follows - 1, Follow.objects.count())

    def test_z_no_orphaned_actions(self):
        actions = self.user1.actor_actions.count()
        self.user2.delete()
        self.assertEqual(actions - 1, self.user1.actor_actions.count())

    def test_generic_relation_accessors(self):
        self.assertEqual(self.user2.actor_actions.count(), 2)
        self.assertEqual(self.user2.target_actions.count(), 1)
        self.assertEqual(self.user2.action_object_actions.count(), 0)

    def test_hidden_action(self):
        testaction = self.user1.actor_actions.all()[0]
        testaction.public = False
        testaction.save()
        self.assertNotIn(testaction, self.user1.actor_actions.public())

    def test_tag_follow_url(self):
        src = '{% follow_url user %}'
        output = render(src, user=self.user1)
        self.assertEqual(output, reverse('actstream_follow', args=(
            self.user_ct.pk, self.user1.pk)))

    def test_tag_follow_url_with_flag(self):
        src = '{% follow_url user "liking" %}'
        output = render(src, user=self.user1)
        self.assertEqual(output, reverse('actstream_follow', kwargs={
            'content_type_id': self.user_ct.pk,
            'object_id': self.user1.pk,
            'flag': 'liking'
        }))

    def test_tag_follow_all_url(self):
        src = '{% follow_all_url user %}'
        output = render(src, user=self.user1)
        self.assertEqual(output, reverse('actstream_follow_all', args=(
            self.user_ct.pk, self.user1.pk)))

    def test_tag_follow_all_url_with_flag(self):
        src = '{% follow_all_url user "liking" %}'
        output = render(src, user=self.user1)
        self.assertEqual(output, reverse('actstream_follow_all', kwargs={
            'content_type_id': self.user_ct.pk,
            'object_id': self.user1.pk,
            'flag': 'liking'
        }))

    def test_tag_actor_url(self):
        src = '{% actor_url user %}'
        output = render(src, user=self.user1)
        self.assertEqual(output, reverse('actstream_actor', args=(
            self.user_ct.pk, self.user1.pk)))

    def test_tag_display_action(self):
        src = '{% display_action action %}'
        output = render(src, action=self.join_action)
        self.assertAllIn([str(self.user1), 'joined', str(self.group)], output)
        src = '{% display_action action as nope %}'
        self.assertEqual(render(src, action=self.join_action), '')

    def test_tag_activity_stream(self):
        output = render('''{% activity_stream 'actor' user as='mystream' %}
        {% for action in mystream %}
            {{ action }}
        {% endfor %}
        ''', user=self.user1)
        self.assertAllIn([str(action) for action in actor_stream(self.user1)],
                         output)

    def test_model_actions_with_kwargs(self):
        """
        Testing the model_actions method of the ActionManager
        by passing kwargs
        """
        self.assertSetEqual(model_stream(self.user1, verb='commented on'), [
            'admin commented on CoolGroup %s ago' % self.timesince,
        ])

    def test_user_stream_with_kwargs(self):
        """
        Testing the user method of the ActionManager by passing additional
        filters in kwargs
        """
        self.assertSetEqual(user_stream(self.user1, verb='joined'), [
            'Two joined CoolGroup %s ago' % self.timesince,
        ])

    def test_is_following_filter(self):
        src = '{% if user|is_following:group %}yup{% endif %}'
        self.assertEqual(render(src, user=self.user2, group=self.group), 'yup')
        self.assertEqual(render(src, user=self.user1, group=self.group), '')

    def test_is_following_tag_with_empty_flag(self):
        src = '{% is_following user group "" as is_following %}' \
              '{% if is_following %}yup{% endif %}'
        self.assertEqual(render(src, user=self.user4, group=self.another_group), 'yup')
        self.assertEqual(render(src, user=self.user1, group=self.another_group), '')

    def test_is_following_tag_with_flag(self):
        src = '{% is_following user group "liking" as is_following %}' \
              '{% if is_following %}yup{% endif %}'
        self.assertEqual(render(src, user=self.user4, group=self.another_group), 'yup')
        self.assertEqual(render(src, user=self.user1, group=self.another_group), '')

    def test_is_following_tag_with_verb_variable(self):
        src = '{% is_following user group verb as is_following %}' \
              '{% if is_following %}yup{% endif %}'
        self.assertEqual(render(src, user=self.user4, group=self.another_group, verb='liking'), 'yup')
        self.assertEqual(render(src, user=self.user1, group=self.another_group, verb='liking'), '')

    def test_none_returns_an_empty_queryset(self):
        qs = Action.objects.none()
        self.assertFalse(qs.exists())
        self.assertEqual(qs.count(), 0)

    def test_with_user_activity(self):
        self.assertNotIn(self.join_action, list(user_stream(self.user1)))
        self.assertIn(self.join_action,
                      list(user_stream(self.user1, with_user_activity=True)))

    def test_store_untranslated_string(self):
        lang = get_language()
        activate('fr')
        verb = _('English')

        self.assertEqual(verb, 'Anglais')
        action.send(self.user1, verb=verb, action_object=self.comment,
                    target=self.group, timestamp=self.testdate)
        self.assertTrue(Action.objects.filter(verb='English').exists())
        activate(lang)
