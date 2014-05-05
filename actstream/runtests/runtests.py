#!/usr/bin/env python

# http://ericholscher.com/blog/2009/jun/29/enable-setuppy-test-your-django-apps/
# http://www.travisswicegood.com/2010/01/17/django-virtualenv-pip-and-fabric/
# http://code.djangoproject.com/svn/django/trunk/tests/runtests.py
# https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/runtests/runtests.py
import os
import sys

# fix sys path so we don't need to setup PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ['DJANGO_SETTINGS_MODULE'] = 'actstream.runtests.settings'

engine = 'django.db.backends.sqlite3'

try:
    engine = sys.argv[1:][0]
except IndexError:
    pass

if engine.startswith('mysql'):
    engine = 'django.db.backends.mysql'
elif engine.startswith('postgre'):
    engine = 'django.db.backends.postgresql_psycopg2'

os.environ['DATABASE_ENGINE'] = engine

try:
    from psycopg2cffi import compat
    compat.register()
except ImportError:
    pass

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

import django
try:
    django.setup()
except AttributeError:
    pass


if __name__ == '__main__':
    from django.conf import settings
    from django.test.utils import get_runner

    sys.exit(get_runner(settings)(interactive=False).run_tests(['actstream', 'testapp']))
