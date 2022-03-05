try:
    from actstream.signals import action
except:
    pass

import django

__version__ = '1.4.0'
__author__ = 'Asif Saif Uddin, Justin Quick <justquick@gmail.com>'

if django.VERSION < (3, 2):
    default_app_config = 'actstream.apps.ActstreamConfig'
