# Django settings for example_project project.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import django

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Justin Quick', 'justquick@gmail.com'),
)

ENGINE = os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3')
DATABASES = {
    'default': {
        'ENGINE': ENGINE,
        'NAME': ':memory:',
        'OPTIONS': {
        }
    }
}

if 'postgres' in ENGINE or 'mysql' in ENGINE:
    USER, PASSWORD = 'test', 'test'
    if os.environ.get('TRAVIS', False):
        if 'mysql' in ENGINE:
            USER, PASSWORD = 'travis', ''
        else:
            USER, PASSWORD = 'postgres', ''
    DATABASES['default'].update(
        NAME='test',
        USER=os.environ.get('DATABASE_USER', USER),
        PASSWORD=os.environ.get('DATABASE_PASSWORD', PASSWORD),
        HOST=os.environ.get('DATABASE_HOST', 'localhost')
    )

print(DATABASES)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'wzf0h@r2u%m^_zgj^39-y(kd%+n+j0r7=du(q0^s@q1asdfasdfasdft%^2!p'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    'templates',
)

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
]

if django.VERSION >= (1, 10):
    TEMPLATE_CONTEXT_PROCESSORS = [
        'django.contrib.auth.context_processors.auth',
        'django.template.context_processors.debug',
        'django.template.context_processors.i18n',
        'django.template.context_processors.media',
        'django.template.context_processors.static',
        'django.template.context_processors.tz',
    ]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': TEMPLATE_CONTEXT_PROCESSORS
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'actstream.runtests.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admindocs',
    'django.contrib.sites',
    'actstream.runtests.testapp',
    'actstream.runtests.testapp_nested',
    'actstream',
)

ACTSTREAM_SETTINGS = {
    'MANAGER': 'actstream.runtests.testapp.streams.MyActionManager',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 0,
}


if django.VERSION[:2] >= (1, 5):
    AUTH_USER_MODEL = 'testapp.MyUser'


try:
    import django.test.simple
except ImportError:
    pass
else:
    TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'
