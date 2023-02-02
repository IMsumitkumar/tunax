# ==================production==============

from pathlib import Path
from django.contrib import messages
import os 

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-9ipkedf_&(lldwqu&#gb%yb!(c82_4bq-gr!&xafw+revy$m)^'

DEBUG = True

ALLOWED_HOSTS = ['*']

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'allauth.socialaccount.providers.discord',
    # 'allauth.socialaccount.providers.facebook', 
    'allauth.socialaccount.providers.google',
    'tournament.apps.TournamentConfig',
    'userprofile.apps.UserprofileConfig',
    'accounts',
    'scrims',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'bootstrap4',
    'crispy_forms',
    'djrichtextfield',
    'django_social_share',
    'imagekit',
    'storages',
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

ROOT_URLCONF = 'battleground.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'battleground.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',    
#     }
# }

# HEROKU DATABASE
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'd80b9t4eikq5gm',
#         'USER': 'kxckyrgftexapi',
#         'HOST': 'ec2-3-209-234-80.compute-1.amazonaws.com',
#         'PASSWORD': '57cf94fca429673590e5210feede8ed962b0182b8262bebee8dc266d16d7e806',
#         'PORT': '5432',
#     }
# }

# # AWS DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'imsumit',
        'PASSWORD': 'kumarsumitK102938',
	    'HOST': "tunax-database.cc8kwkseyqnw.ap-south-1.rds.amazonaws.com",
        'PORT': '5432',
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'staticfiles' 


CRISPY_TEMPLATE_PACK = 'bootstrap4'
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',

}

BASE_URL = "http://65.0.73.127/"
# BASE_URL = "http://rewardo.ga/"
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True


CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'realme5sumit@gmail.com'
EMAIL_HOST_PASSWORD = 'eiukbjsfkntpuvac'  
EMAIL_PORT = 587

CELERY_BROKER_URL = 'amqp://localhost'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'

DJRICHTEXTFIELD_CONFIG = {
    'js': ['//cdn.tiny.cloud/1/no-api-key/tinymce/5/tinymce.min.js'],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': False,
        'plugins': 'link image',
        'toolbar': 'bold italic | link image | removeformat',
        'width': 700
    }
}


SITE_ID = 1
LOGIN_REDIRECT_URL = "/"

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_ACCESS_KEY_ID = 'AKIASWYGFVINOBSBP2GY'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'rewardo-media'

AWS_QUERYSTRING_AUTH = False

