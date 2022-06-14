.. _feeds:

Feeds
=====

The app supports feeds that support the `Atom Activity Streams 1.0 <http://activitystrea.ms/specs/atom/1.0/>`_
and `JSON Activity Streams 1.0 <http://activitystrea.ms/specs/json/1.0/>`_ specifications.



Builtin Feed URLs
-----------------

If you register the app with this URL prefix you can obtain the feeds using the URLs below.

.. code-block:: python

    url('^activity/', include('actstream.urls'))

:ref:`user-stream`

Shows user stream for currently logged in user.

.. code-block:: bash

    /activity/feed/atom/
    /activity/feed/json/

If you want to include the user own activity, the optional parameter ``with_user_activity`` can be passed to the user stream as a query string parameter:

.. code-block:: bash

    /activity/feed/atom/?with_user_activity=true
    /activity/feed/json/?with_user_activity=true
 

:ref:`any-stream`

.. code-block:: bash

    /activity/feed/<content_type_id>/<object_id>/atom/
    /activity/feed/<content_type_id>/<object_id>/json/

:ref:`model-stream`

.. code-block:: bash

    /activity/feed/<content_type_id>/atom/
    /activity/feed/<content_type_id>/json/



Custom JSON Feed URLs
---------------------

Custom JSON feeds based on your custom streams registered by :ref:`custom-streams`

.. code-block:: python

    # myapp/urls.py
    from actstream.feeds import CustomJSONActivityFeed
    url(r'^feeds/mystream/(?P<verb>.+)/$',
        CustomJSONActivityFeed.as_view(name='mystream'))


Output
------

JSON
^^^^

Here is some sample output of the JSON feeds.
The formatting and attributes can be customized by subclassing :class:`actstream.feeds.AbstractActivityStream`

.. code-block:: json

    {
        "totalItems": 1
        "items": [
            {
                "actor": {
                    "id": "tag:example.com,2000-01-01:/activity/actors/13/2/",
                    "displayName": "Two",
                    "objectType": "my user",
                    "url": "http://example.com/activity/actors/13/2/"
                },
                "target": {
                    "id": "tag:example.com,2000-01-01:/activity/actors/2/1/",
                    "displayName": "CoolGroup",
                    "objectType": "group",
                    "url": "http://example.com/activity/actors/2/1/"
                },
                "verb": "joined",
                "id": "tag:example.com,2000-01-01:/activity/detail/3/",
                "published": "2000-01-01T00:00:00Z",
                "url": "http://example.com/activity/detail/3/"
            }
        ]
    }


ATOM
^^^^

Here is some sample output of the ATOM feeds.
They are based on the Django syndication framework and you can subclass :class:`actstream.feeds.ActivityStreamsBaseFeed` or any of its subclasses to modify the formatting.

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <feed xmlns:activity="http://activitystrea.ms/spec/1.0/" xml:lang="en-us"
          xmlns="http://www.w3.org/2005/Atom">
        <title>Activity feed for your followed actors</title>
        <link href="http://example.com/actors/14/1/" rel="alternate"></link>
        <link href="http://example.com/feed/atom/" rel="self"></link>
        <id>http://example.com/actors/14/1/</id>
        <updated>2014-08-31T12:42:05Z</updated>
        <subtitle>Public activities of actors you follow</subtitle>
        <entry>
            <uri>http://example.com/detail/3/</uri>
            <link type="text/html" href="http://example.com/detail/3/"
                  rel="alternate"></link>
            <activity:verb>joined</activity:verb>
            <published>2000-01-01T00:00:00Z</published>
            <id>tag:example.com,2000-01-01:/detail/3/</id>
            <title>Two joined CoolGroup 14 years, 8 months ago</title>
            <author>
                <id>tag:example.com,2000-01-01:/actors/14/2/</id>
                <activity:object-type>my user</activity:object-type>
                <name>Two</name>
            </author>
            <activity:target>
                <id>tag:example.com,2000-01-01:/actors/2/1/</id>
                <activity:object-type>group</activity:object-type>
                <title>CoolGroup</title>
            </activity:target>
        </entry>
    </feed>



