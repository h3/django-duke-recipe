from paraskiflex.settings import *

DEV = False
DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '%(project)s',
        'USER': '%(project)s',
        'PASSWORD': '',
    },
}
