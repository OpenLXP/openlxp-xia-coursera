"""
Django settings for openlxp_xia_coursera project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import mimetypes
import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY_VAL')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

mimetypes.add_type("text/css", ".css", True)

ALLOWED_HOSTS = os.environ.get('HOSTS').split(';')

# Application definition

INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'openlxp_xia',
    'openlxp_notifications',
    # 'openlxp_P1_notification',
    'django_celery_beat',
    'django_celery_results',
    'health_check',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'openlxp_P1_notification.middleware.TemplateMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = ['health/', 'api/health/']
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_BROWSER_XSS_FILTER = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

ROOT_URLCONF = 'openlxp_xia_coursera_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'openlxp_xia_coursera_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': 3306,
        'OPTIONS': {
            'ssl_disabled': True,
            'sql_mode': 'STRICT_TRANS_TABLES'
            }
    }
}


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

EMAIL_BACKEND = 'django_ses.SESBackend'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_CACHE_BACKEND = 'default'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}
EMAIL_BACKEND = 'django_ses.SESBackend'
LOG_PATH = os.environ.get('LOG_PATH')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'loggers': {
        'dict_config_logger': {
            'handlers': ['console', 'file_logs'],
            'level': 'INFO',
            'propagate': True,
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simpleRe',
        },
        'file_logs': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': LOG_PATH,
            'formatter': 'simpleRe',
        },

    },

    'formatters': {
        'simpleRe': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        }
    }
}

# Directory to store files during upload scanning

if os.environ.get('TMP_SOURCE_DIR') is not None and\
        len(os.environ.get('TMP_SOURCE_DIR')) > 0:
    TMP_SOURCE_DIR = os.environ.get('TMP_SOURCE_DIR')
else:
    TMP_SOURCE_DIR = os.path.join(BASE_DIR, 'tmp', 'source')
TMP_SOURCE_DIR = os.path.join(TMP_SOURCE_DIR, '')
