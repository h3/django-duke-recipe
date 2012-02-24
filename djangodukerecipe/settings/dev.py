# Development environment settings

from %(project_name)s.conf.settings.default import *

import getpass

TEMPLATE_LOADERS = (
    # Remove cached template loader
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

#DISABLED_APPS = ['sentry.client', 'sentry']

DEBUG = True

DATABASE_PREFIX = ''
DATABASE_USER = getpass.getuser()
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = None

for k, v in DATABASES.iteritems():
    DATABASES[k].update({
        'NAME': DATABASE_PREFIX + v['NAME'],
        'HOST': DATABASE_HOST,
        'PORT': DATABASE_PORT,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'OPTIONS': {
            'autocommit': False
        }
    })

# django-devserver: http://github.com/dcramer/django-devserver
#try:
#    import devserver
#except ImportError:
#    pass
#else:
#    INSTALLED_APPS = INSTALLED_APPS + (
#        'devserver',
#    )
#    DEVSERVER_IGNORED_PREFIXES = ['/media', '/uploads']
#    DEVSERVER_MODULES = (
#        # 'devserver.modules.sql.SQLRealTimeModule',
#        # 'devserver.modules.sql.SQLSummaryModule',
#        # 'devserver.modules.profile.ProfileSummaryModule',
#        # 'devserver.modules.request.SessionInfoModule',
#        # 'devserver.modules.profile.MemoryUseModule',
#        # 'devserver.modules.profile.LeftOversModule',
#        # 'devserver.modules.cache.CacheSummaryModule',
#    )


#INSTALLED_APPS = (
#    'south',
#) + INSTALLED_APPS

#MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
#    'disqus.middleware.profile.ProfileMiddleware',
#)

CACHE_BACKEND = 'locmem://'
