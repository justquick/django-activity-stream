import os

try:
    import debug_toolbar as DEBUG_TOOLBAR
except:
    DEBUG_TOOLBAR = None

try:
    import rest_framework as DRF
except:
    DRF = None

# Always for debugging, dont use the runtests app in production!
DEBUG = True

ADMINS = (
    ('Justin Quick', 'justquick@gmail.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
        }
    }
}

if os.environ.get('GITHUB_WORKFLOW', False):
    DATABASE_ENGINE = os.environ.get('DATABASE_ENGINE', 'sqlite')
    if 'mysql' in DATABASE_ENGINE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'test',
                'USER': 'root',
                'PASSWORD': '',
                'HOST': '127.0.0.1',
                'PORT': '3306',
            },
        }
    elif 'postgres' in DATABASE_ENGINE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'postgres',
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'HOST': '127.0.0.1',
                'PORT': '5432',
            },
        }
    elif 'file' in DATABASE_ENGINE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'db.sqlite3',
            },
        }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia. org/wiki/List_of_tz_zones_by_name
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
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = 'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: 'http://media.lawrence.com', 'http://example.com/media/'
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


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admindocs',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',


    'actstream',

    'testapp',
    'testapp_nested',
]

try:
    import debug_toolbar
except:
    pass
else:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

try:
    import rest_framework
except:
    pass
else:
    INSTALLED_APPS.extend(['rest_framework', 'generic_relations'])


try:
    import django_extensions
except:
    pass
else:
    INSTALLED_APPS.append('django_extensions')

STATIC_URL = '/static/'
STATIC_ROOT = 'static'

ACTSTREAM_SETTINGS = {
    'MANAGER': 'testapp.streams.MyActionManager',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 0,
    'DRF': {
        'SERIALIZERS': {
            'auth.Group': 'testapp.drf.GroupSerializer',
            'testapp.MyUser': 'testapp.drf.MyUserSerializer'
        },
        'VIEWSETS': {
            'auth.Group': 'testapp.drf.GroupViewSet'
        },
        'PERMISSIONS': {
            'testapp.MyUser': ['rest_framework.permissions.IsAdminUser']
        }
    }
}

AUTH_USER_MODEL = 'testapp.MyUser'


REST_FRAMEWORK = {
}

try:
    import drf_spectacular
except:
    pass
else:
    INSTALLED_APPS.extend(['drf_spectacular'])
    REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Activity Streams API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '0.0.0',
    'EXTERNAL_DOCS': {'url': '', 'description': ''},
    'CONTACT': {'name': '', 'email': ''},
}
