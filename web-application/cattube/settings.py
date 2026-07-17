import os
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured
# Never put credentials in your code!
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9tf$jps6u-rxnv8nuur=*z&44$d!*_k@9td4jfaurtd5)xu_50'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'storages',

    'cattube.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cattube.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'cattube/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cattube.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'cattube/static'),
]

def required_env(name):
    value = os.environ.get(name)
    if value:
        return value
    raise ImproperlyConfigured(f'Missing required environment variable: {name}')


def public_url_settings(public_url_base):
    parsed = urlsplit(public_url_base.rstrip('/'))
    if not parsed.scheme or not parsed.netloc:
        raise ImproperlyConfigured(
            'B2_PUBLIC_URL_BASE must include a URL scheme and host, '
            'for example https://f001.backblazeb2.com/file/my-public-bucket'
        )
    return f'{parsed.scheme}:', f'{parsed.netloc}{parsed.path.rstrip("/")}'


# Set these in a .env file or as environment variables
B2_APPLICATION_KEY_ID = required_env('B2_APPLICATION_KEY_ID')
B2_APPLICATION_KEY = required_env('B2_APPLICATION_KEY')
B2_BUCKET_NAME = required_env('B2_BUCKET_NAME')
B2_PRIVATE_BUCKET_NAME = required_env('B2_PRIVATE_BUCKET_NAME')
B2_REGION = required_env('B2_REGION')
B2_PUBLIC_URL_BASE = required_env('B2_PUBLIC_URL_BASE').rstrip('/')
TRANSCODER_WEBHOOK = required_env('TRANSCODER_WEBHOOK')

B2_STORAGE_ENDPOINT_HOST = f's3.{B2_REGION}.backblazeb2.com'
B2_STORAGE_ENDPOINT_URL = f'https://{B2_STORAGE_ENDPOINT_HOST}'
# Keep this value mirrored in worker/app.py so both deployables identify the sample.
B2_USER_AGENT_EXTRA = 'b2-video-sharing-example (backblaze-b2-samples)'
B2_PUBLIC_URL_PROTOCOL, B2_PUBLIC_URL_LOCATION = public_url_settings(B2_PUBLIC_URL_BASE)

B2_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

B2_STATIC_LOCATION = 'static'
STATICFILES_STORAGE = 'cattube.storage_backends.StaticStorage'
STATIC_URL = f'{B2_PUBLIC_URL_BASE}/{B2_STATIC_LOCATION}/'

B2_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'cattube.storage_backends.PublicMediaStorage'

B2_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'cattube.storage_backends.PrivateMediaStorage'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

LOGOUT_REDIRECT_URL = 'home'
