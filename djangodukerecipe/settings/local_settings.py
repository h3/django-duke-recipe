from %(project)s.conf.settings.dev import *

# disable sentry
#DISABLED_APPS = ['sentry']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev.db',
    }
}
