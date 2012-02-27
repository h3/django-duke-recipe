import os, sys, imp

sys.path.append('../')

def main(settings_module='settings'):
    print "A"
    if settings_module:
        print "B"
        settings_module = settings_module
       #os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    else:
        print "C"
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'settings')
    imp.find_module(settings_module)
    try:
        print "D"
        print settings_module
        imp.find_module(settings_module)
    except ImportError, e:
        print "E"
        print sys.path
        sys.stderr.write("Error loading the settings module '%s': %s"
                            % (settings_module, e))
        return sys.exit(1)

    from django.core.management import execute_from_command_line
    print "F"
    execute_from_command_line(sys.argv)
