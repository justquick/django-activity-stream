from django.core.exceptions import ImproperlyConfigured

from actstream.settings import get_follow_model


def delete_orphaned_follows(sender, instance=None, **kwargs):
    """
    Clean up Follow objects that refer to a Django object that's being deleted
    """
    if str(sender._meta) == 'migrations.migration':
        return

    try:
        get_follow_model().objects.for_object(instance).delete()
    except ImproperlyConfigured:  # raised by actstream for irrelevant models
        pass
