"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 5.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# my addition to imports (used on next addition)
import sys
import os
import dj_database_url
import logging

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the value of the environment variable 'IS_REMOTE' and store it in is_remote_flag
print("IS_REMOTE is set to:", os.getenv('IS_REMOTE', 'NOT SET'))
is_remote_flag = os.getenv('IS_REMOTE', 'false').lower() == 'true'

# Set DEBUG to True, both locally and remotely
# idc swap to 'DEBUG = not is_remote_flag' to enable DEBUG locally, but disable DEBUG remotely
DEBUG = True

# Log the values of the environment variables for debugging
logging.debug(f"IS_REMOTE: {is_remote_flag}")
logging.debug(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

SECRET_KEY = os.getenv('SECRET_KEY')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-!$nwz7ku_wr%k+vipn*_419-qi(@t=)!gi!1jh4gw)pj@iia#_'
# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True

ALLOWED_HOSTS = ['data-driven-forms.onrender.com','localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tester', # this one from RD
    'app1', # this one from RD
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'main.urls'

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

WSGI_APPLICATION = 'main.wsgi.application'

# My amendments to database settings based on whether we're running remotely or locally
if is_remote_flag:
    # Remote database (via DATABASE_URL)
    logging.debug("Running in remote environment, using DATABASE_URL.")
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Local database settings
    logging.debug("Running in local environment, using local database settings.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'data_driven_forms',
            'USER': 'robert',
            'PASSWORD': 'downingstreet',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
#
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Ensures Django knows where to find static files in development
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "app1/static/app1"),
]

# Ensures Django knows where to find files in production (Only needed for collectstatic)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_COOKIE_AGE = 86400  # 24 hours (86400 seconds)
# Note default setting is SESSION_EXPIRE_AT_BROWSER_CLOSE = False so the command above keeps things tidy.