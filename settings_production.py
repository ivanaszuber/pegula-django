#
# Production Django settings for Pegula `backend`
#
# To use these settings rather than the dev defaults:
#
# $> DJANGO_SETTINGS_MODULE=authservice.settings_production django-admin.py foo
#
# We also
#
#
# TODO: Re-review https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

import os

from .settings import *


DEBUG = True

# See: https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-ALLOWED_HOSTS
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     'backend',
        'USER':     os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'INSECURE_Ye3P8FLwaL'),
        'HOST':     'authdb',  # Docker configures /etc/hosts when we link containers
        'PORT':     os.environ.get('AUTHDB_PORT_5432_TCP_PORT', '5432'),
    }
}


# Enforce SSL connections exclusively (unless our gateway is doing SSL termination?)
CSRF_COOKIE_SECURE = False

# To be able to run authservice on a local vm for development (which does not use SSL). We have disabled the enforcement
# of secure session cookies as the nginx gateway enforces SSL always.
# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SESSION_COOKIE_SECURE
# SESSION_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')