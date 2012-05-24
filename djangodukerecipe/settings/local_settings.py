from %(project)s.conf.settings.dev import *

DEBUG_TOOLBAR = False

# disable sentry
#DISABLED_APPS = ['sentry']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev.db',
    }
}

if DEBUG_TOOLBAR:
    INTERNAL_IPS = ('127.0.0.1', '0.0.0.0', 'dev')
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
