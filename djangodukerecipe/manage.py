import os, sys, imp

def main(settings_module='settings'):
    if settings_module:
        settings_module = settings_module
       #os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    else:
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'settings')

    try:
        imp.find_module(settings_module)
        try:
            imp.find_module(settings_module)
        except ImportError, e:
            sys.stderr.write("Error loading the settings module '%s': %s"
                                % (settings_module, e))
            return sys.exit(1)
    except ImportError, e:
        sys.stdout.write("Warning, no settings module named '%s': %s"
                            % (settings_module, e))


    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
