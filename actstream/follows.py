from django.core.exceptions import ImproperlyConfigured

from actstream.models import Follow


def delete_orphaned_follows(sender, instance=None, **kwargs):
    """
    Clean up Follow objects that refer to a Django object that's being deleted
    """
    if str(sender._meta) == 'migrations.migration':
        return

    try:
        Follow.objects.for_object(instance).delete()
    except ImproperlyConfigured:  # raised by actstream for irrelevant models
        pass
