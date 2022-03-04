import os

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

    'mysite.core',
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

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'mysite/templates')],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'


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
    os.path.join(BASE_DIR, 'mysite/static'),
]

# Change these to match your configuration
AWS_ACCESS_KEY_ID = '<your b2 application key id>'
AWS_SECRET_ACCESS_KEY = '<your b2 application key>'
AWS_PRIVATE_BUCKET_NAME = '<a private bucket>'
AWS_STORAGE_BUCKET_NAME = '<a public bucket>'
AWS_S3_REGION_NAME = '<your b2 region - e.g. us-west-001>'

AWS_S3_ENDPOINT = f's3.{AWS_S3_REGION_NAME}.backblazeb2.com'
AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_ENDPOINT}'

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_STATIC_LOCATION = 'static'
STATICFILES_STORAGE = 'mysite.storage_backends.StaticStorage'
STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_ENDPOINT}/"

AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
DEFAULT_FILE_STORAGE = 'mysite.storage_backends.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = 'mysite.storage_backends.PrivateMediaStorage'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'myvideos'

# Change this to point to your transcoder worker
TRANSCODER_WEBHOOK = 'http://<your transcoder hostname>/videos'