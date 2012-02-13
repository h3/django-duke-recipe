import os
from django.core import management
 
def main(settings_module):
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
    from django.core.handlers.wsgi import WSGIHandler
    return WSGIHandler()
