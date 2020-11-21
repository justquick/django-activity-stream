from django.conf import settings
from django.utils.feedgenerator import rfc3339_date

from actstream.tests import base


class FeedsTestCase(base.DataTestCase):
    urls = 'actstream.urls'

    @property
    def rss_base(self):
        return ['<?xml version="1.0" encoding="utf-8"?>\n', '<rss ',
                'xmlns:atom="http://www.w3.org/2005/Atom"', 'version="2.0"',
                '<language>%s' % settings.LANGUAGE_CODE]

    @property
    def atom_base(self):
        return ['<?xml version="1.0" encoding="utf-8"?>\n',
                'xmlns="http://www.w3.org/2005/Atom"',
                'xml:lang="%s"' % settings.LANGUAGE_CODE,
                '<uri>http://example.com/detail/',
                '<id>tag:example.com,2000-01-01:/detail/']

    def test_feed(self):
        self.client.login(username='admin', password='admin')
        expected = [
            'Activity feed for your followed actors',
            'Public activities of actors you follow',
            'Two started following CoolGroup %s ago' % self.timesince,
            'Two joined CoolGroup %s ago' % self.timesince,
        ]
        expected_json = expected[2:]
        expected_json_with_user_activity = expected_json + ['admin started following Two %s ago' % self.timesince,
        'admin joined CoolGroup %s ago' % self.timesince,
        'admin commented on CoolGroup %s ago' % self.timesince
        ]
        rss = self.capture('actstream_feed')
        self.assertAllIn(self.rss_base + expected, rss)
        atom = self.capture('actstream_feed_atom')
        self.assertAllIn(self.atom_base + expected, atom)
        json = self.capture('actstream_feed_json')
        self.assertAllIn(expected_json, json)
        json_with_user_activity = self.capture('actstream_feed_json', query_string='with_user_activity=true') 
        self.assertAllIn(expected_json_with_user_activity, json_with_user_activity) 

    def test_model_feed(self):
        expected = [
            'Activity feed from %s' % self.User.__name__,
            'Public activities of %s' % self.User.__name__,
            'admin commented on CoolGroup %s ago' % self.timesince,
            'Two started following CoolGroup %s ago' % self.timesince,
            'Two joined CoolGroup %s ago' % self.timesince,
            'admin started following Two %s ago' % self.timesince,
            'admin joined CoolGroup %s ago' % self.timesince,
        ]
        rss = self.capture('actstream_model_feed', self.user_ct.pk)
        self.assertAllIn(self.rss_base + expected, rss)
        atom = self.capture('actstream_model_feed_atom', self.user_ct.pk)
        self.assertAllIn(self.atom_base + expected, atom)
        json = self.capture('actstream_model_feed_json', self.user_ct.pk)

    def test_object_feed(self):
        expected = [
            'Activity for Two',
            'admin started following Two %s ago' % self.timesince,
        ]
        rss = self.capture('actstream_object_feed',
                           self.user_ct.pk, self.user2.pk)
        self.assertAllIn(self.rss_base + expected, rss)
        atom = self.capture('actstream_object_feed_atom',
                            self.user_ct.pk, self.user2.pk)
        self.assertAllIn(self.atom_base + expected, atom)
        json = self.capture(
            'actstream_object_feed_json',
            self.user_ct.pk, self.user2.pk
        )
