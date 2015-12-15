Templatetags
------------

Start off your templates by adding the following load tag.

.. code-block:: django

    {% load activity_tags %}

Displaying Streams
==================

You can use the ``activity_stream`` templatetag to render any of the builtin streams or your own custom streams.
The first argument is the name of the stream method and then other arguments are passed from your templates into the stream functions.


.. code-block:: django

    {% activity_stream 'actor' user %}
    {% for action in stream %}
        {% display_action action %}
    {% endfor %}


You can also access custom streams by name in the same way.
The tag puts the resulting queryset into a context variable which is by default simply called ``stream`` but you can customize the name by passing a value for the ``as`` keyword argument.

.. code-block:: django

    {% activity_stream 'mystream' request.user 'commented' as='mycomments' %}
    {% for action in mycomments %}
        {% display_action action %}
    {% endfor %}


Both examples above use the ``display_action`` templatetag which is an include tag which passes the ``action`` variable to ``actstream/action.html``.
You can override it to make it render as you would like.

Follow/Unfollow
===============

There are two templatetags which are helpful for rendering information for following and unfollowing entities.
The first is ``follow_url`` which returns the url you can hit to either follow the entity if you are not following it or unfollow if you are following it.
There is also a ``is_following`` template filter which returns True if the user is following the given entity.
The end result is a link that is a toggle.

.. code-block:: django

    <a href="{% follow_url other_user %}">
        {% if request.user|is_following:other_user %}
            stop following
        {% else %}
            follow
        {% endif %}
    </a>

The code above will generate the url for the user to only follow actions where the object is the target. If you want the user to follow an object as both actor and target, you need to use the ``follow_all_url`` tag.

.. code-block:: django

    <a href="{% follow_all_url other_user %}">
        {% if request.user|is_following:other_user %}
            stop following
        {% else %}
            follow
        {% endif %}
    </a>
