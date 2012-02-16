"""
Django development settings
"""

import os, sys
from %(project)s.%(settings)s import *

DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False
EMAIL_DEBUG = True
PIPELINE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'dev.db'),
    },
}

# Warning: this breaks the admin
#TEMPLATE_STRING_IF_INVALID = '{! Variable not found !}'

if EMAIL_DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    #DEFAULT_FROM_EMAIL = 'dev@email.com'
    #NOTIFICATION_EMAIL = ['dev1@email.com', 'dev2@email.com']


if DEBUG_TOOLBAR:
    INTERNAL_IPS = ('127.0.0.1', '0.0.0.0')
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)


if PIPELINE:
    STATICFILES_FINDERS = (
      'pipeline.finders.PipelineFinder',
      'django.contrib.staticfiles.finders.FileSystemFinder',
      'django.contrib.staticfiles.finders.AppDirectoriesFinder'
    )
    PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('pipeline.middleware.MinifyHTMLMiddleware',)
    PIPELINE_STORAGE = 'pipeline.storage.PipelineFinderStorage'
