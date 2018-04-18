import os

DEBUG = True

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
SECRET_KEY = 'secret-key'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]
    },
}]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admindocs',
    'django.contrib.sites',
    'testapp',
    'testapp_nested',
    'actstream',
)

ACTSTREAM_SETTINGS = {
    'MANAGER': 'testapp.streams.MyActionManager',
    'VERB_TRANSFORMER':'actstream.tests.base.TestVerbTransformer',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 0,
}

AUTH_USER_MODEL = 'testapp.MyUser'
