#!/usr/bin/env python

# http://ericholscher.com/blog/2009/jun/29/enable-setuppy-test-your-django-apps/
# http://www.travisswicegood.com/2010/01/17/django-virtualenv-pip-and-fabric/
# http://code.djangoproject.com/svn/django/trunk/tests/runtests.py
# https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/runtests/runtests.py
import os
import sys

# fix sys path so we don't need to setup PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
os.environ['DJANGO_SETTINGS_MODULE'] = 'actstream.runtests.settings'

from django.conf import settings
from django.core.management import execute_from_command_line

import mock

if __name__ == '__main__':

    default_labels = ['actstream', 'testapp']

    argv = ['manage.py', 'test'] + sys.argv[1:]
    for a in sys.argv:
        if [x for x in default_labels if a.startswith(x)]:
            break
    else:
        argv += default_labels

    with mock.patch('django.utils.timesince.avoid_wrapping', lambda x: x):
        sys.exit(execute_from_command_line(argv))
