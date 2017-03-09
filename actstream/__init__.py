try:
    from actstream.settings import ACTSTREAM_ACTION_MODEL, ACTSTREAM_FOLLOW_MODEL
    from actstream.signals import action
    from django.apps import apps as django_apps
except:
    pass


__version__ = '0.6.3'
__author__ = 'Justin Quick <justquick@gmail.com>'
default_app_config = 'actstream.apps.ActstreamConfig'


def get_action_model():
    """
    Returns the Action model that is active in this project.
    """
    try:
        return django_apps.get_model(ACTSTREAM_ACTION_MODEL)
    except ValueError:
        raise ImproperlyConfigured("ACTSTREAM_ACTION_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ACTSTREAM_ACTION_MODEL refers to model '%s' that has not been installed" % ACTSTREAM_ACTION_MODEL
        )


def get_follow_model():
    """
    Returns the Follow model that is active in this project.
    """
    try:
        return django_apps.get_model(ACTSTREAM_FOLLOW_MODEL)
    except ValueError:
        raise ImproperlyConfigured("ACTSTREAM_FOLLOW_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "ACTSTREAM_FOLLOW_MODEL refers to model '%s' that has not been installed" % ACTSTREAM_FOLLOW_MODEL
        )
