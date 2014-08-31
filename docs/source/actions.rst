
Generating Actions
===================

Generating actions can be done using `Django signals <https://docs.djangoproject.com/en/dev/topics/signals/>`__.
A special ``action`` signal is provided for creating the actions.

.. code-block:: python

    from django.db.models.signals import post_save
    from actstream import action
    from myapp.models import MyModel

    # MyModel has been registered with actstream.registry.register

    def my_handler(sender, instance, created, **kwargs):
        action.send(instance, verb='was saved')

    post_save.connect(my_handler, sender=MyModel)

To generate an action anywhere in your code, simply import the action signal and send it with your actor, verb, target, and any other important arguments.

.. code-block:: python

    from actstream import action
    from myapp.models import Group, Comment

    # User, Group & Comment have been registered with
    # actstream.registry.register

    action.send(request.user, verb='reached level 10')

    ...

    group = Group.objects.get(name='MyGroup')
    action.send(request.user, verb='joined', target=group)

    ...

    comment = Comment.create(text=comment_text)
    action.send(request.user, verb='created comment', action_object=comment, target=group)


Actions are stored in a single table in the database using `Django's ContentType framework <https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/>`_
and `GenericForeignKeys <https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/#django.contrib.contenttypes.fields.GenericForeignKey>`_ to create associations with different models in your project.

Actions are generated in a manner independent of how you wish to query them so they can be queried later to generate different streams based on all possible associations.

