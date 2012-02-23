Generating Actions
===================

Generating actions is probably best done in a separate signal.

.. code-block:: python

    from django.db.models.signals import post_save
    from actstream import action
    from myapp.models import MyModel

    def my_handler(sender, instance, created, **kwargs):
        action.send(instance, verb='was saved')

    post_save.connect(my_handler, sender=MyModel)

To generate an action anywhere in your code, simply import the action signal and send it with your actor, verb, and target.

.. code-block:: python

    from actstream import action

    action.send(request.user, verb='reached level 10')
    action.send(request.user, verb='joined', target=group)
    action.send(request.user, verb='created comment', action_object=comment, target=group)
