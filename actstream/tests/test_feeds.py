from django.conf import settings

from actstream.tests import base


class FeedsTestCase(base.DataTestCase):
    urls = 'actstream.urls'
    actstream_models = ('auth.User', 'auth.Group', 'sites.Site')
    rss_base = ['<?xml version="1.0" encoding="utf-8"?>\n', '<rss ',
                'xmlns:atom="http://www.w3.org/2005/Atom"', 'version="2.0"']
    atom_base = ['<?xml version="1.0" encoding="utf-8"?>\n',
                 'xmlns="http://www.w3.org/2005/Atom"',
                 'xml:lang="%s"' % settings.LANGUAGE_CODE]

    def test_feed(self):
        self.client.login(username='admin', password='admin')
        expected = [
            'Activity feed for your followed actors',
            'Public activities of actors you follow',
            'Two started following CoolGroup %s ago' % self.timesince,
            'Two joined CoolGroup %s ago' % self.timesince,
        ]
        rss = self.capture('/feed/')
        self.assertAllIn(self.rss_base + expected, rss)
        atom = self.capture('/feed/atom/')
        self.assertAllIn(self.atom_base + expected, atom)

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
        rss = self.capture('/feed/%s/' % self.user_ct.pk)
        self.assertAllIn(self.rss_base + expected, rss)
        atom = self.capture('/feed/%s/atom/' % self.user_ct.pk)
        self.assertAllIn(self.atom_base + expected, atom)

    def test_object_feed(self):
        expected = [
            'Activity for Two',
            'admin started following Two %s ago' % self.timesince,
        ]
        rss = self.capture('/feed/%s/%s/' % (self.user_ct.pk, self.user2.pk))
        self.assertAllIn(self.rss_base + expected, rss)
        atom = self.capture('/feed/%s/%s/atom/' % (self.user_ct.pk, self.user2.pk))
        self.assertAllIn(self.atom_base + expected, atom)