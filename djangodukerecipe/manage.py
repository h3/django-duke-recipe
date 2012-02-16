from django.core import management
import os,imp

def main(settings_module=None):
    settings_module = settings_module \
            or os.environ.get('DJANGO_SETTINGS_MODULE', 'settings')
    try:
        imp.find_module(settings_module)
    except ImportError, e:
        import sys
        sys.stderr.write("Error loading the settings module '%s': %s"
                            % (settings_module, e))
        return sys.exit(1)

    utility = management.ManagementUtility()
    utility.execute()
