import os

# Django settings for rek project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'admin@rekvizitka.ru'),
    )

SITE_DOMAIN_NAME = 'rekvizitka.ru'
PRODUCTION = False

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'Europe/Moscow'
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')

COMBO_LOADER_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../rekmedia/modules/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '***'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    )

ROOT_URLCONF = 'rek.admin_urls'

CUR_FOLDER = os.path.dirname(__file__)
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(CUR_FOLDER, 'templates').replace('\\','/'),
    os.path.join(CUR_FOLDER, 'client_side').replace('\\','/'),
    )

INSTALLED_APPS = (
    'django.contrib.sessions',

    'rek.admin',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'rek.mango.context_processor.auth',
    'rek.utils.context_processors.rek'
    )

USE_TZ = True

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = 'noreply@rekvizitka.ru'
EMAIL_HOST_PASSWORD = '***'

LOGIN_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/'

#for default company logo (full RekLogo class in models.py)
REK_LOGO = 'img/rek_default_logo.png'
#for search and for rek_code_util
REK1_CODE = 'CE9E'

#for recommendation system
RECOMMENDATION_QUANTITY = 5
RECOMMENDATION_LIFETIME_DAYS = 7

#for mongo db mail messages system
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_DB_NAME = 'rekvizitka'
MONGODB_USER = '***'
MONGODB_PASSWORD = '***'

SESSION_ENGINE = 'rek.mango.session'
AUTHENTICATION_BACKENDS = ('rek.mango.auth.Backend',)

TEST_RUNNER = 'rek.tests.runner.MongoDBTestRunner'
TEST_RUN = False

COMPANY_REK_ID_REGEX = "[abcehkmoprtxABCEHKMOPRTX1234567890]+"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        }
}

CLIENT_SIDE_MODULES_DATA_FILE = os.path.normpath(os.path.join(CUR_FOLDER, '../rekmedia/modules/modules.json'))
CLIENT_SIDE_APPS_DATA_FILE = os.path.normpath(os.path.join(CUR_FOLDER, '../rekmedia/modules/apps.json'))

CLIENT_SIDE_APPS_PATH = '/dmedia/apps/'

# Leave the following lines as last lines of settings file!
try:
    from admin_local_settings import *
except Exception:
    pass
