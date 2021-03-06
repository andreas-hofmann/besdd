"""
Django settings for project_common project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGIN_REDIRECT_URL="/"
LOGOUT_REDIRECT_URL="/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

try:
    with open(os.path.join(BASE_DIR, 'secret_key.txt')) as f:
        SECRET_KEY = f.read().strip()
except FileNotFoundError:
    print("Missing secret key!")
    print("Please generate one, e.g.:")
    print("dd if=/dev/urandom count=1 bs=56 | base64 > secret_key.txt")
    sys.exit(1)

DEBUG = True

if DEBUG == True:
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = ["besdd.de"]
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "same-origin"

# Application definition

INSTALLED_APPS = [
    'slogger.apps.SloggerConfig',
    'registration.apps.RegistrationConfig',

    'bootstrap4',
    'bootstrap_datepicker_plus',
    'crispy_forms',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
FRONTEND_DIST_DIR = os.path.join(FRONTEND_DIR, "dist")

USE_VUE_FRONTEND = False

if DEBUG:
    if os.path.exists(FRONTEND_DIR):
        USE_VUE_FRONTEND = True
else:
    if os.path.exists(FRONTEND_DIST_DIR):
        USE_VUE_FRONTEND = True

if DEBUG and USE_VUE_FRONTEND:
    INSTALLED_APPS.append('webpack_loader')
    WEBPACK_LOADER = {
        'DEFAULT': {
            'CACHE': DEBUG,
            'BUNDLE_DIR_NAME': 'bundles/',  # must end with slash
            'STATS_FILE': os.path.join(FRONTEND_DIR, 'webpack-stats.json'),
        }
    }

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project_common.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates') ],
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

WSGI_APPLICATION = 'project_common.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'CET'

USE_I18N = False

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + "/staticfiles/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

if USE_VUE_FRONTEND and not DEBUG:

    STATICFILES_DIRS.append(FRONTEND_DIST_DIR)
    TEMPLATES[0]['DIRS'].append(FRONTEND_DIST_DIR)