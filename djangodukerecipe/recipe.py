from random import choice
import logging
import os
import subprocess
import shutil

from zc.recipe.egg import Egg
import zc.buildout.easy_install

logger = logging.getLogger(__name__)


DIR = os.path.dirname(__file__)

def template(n):
    return "".join(open(os.path.join(DIR, n)).readlines())

WSGI_TEMPLATE             = template('wsgi.py')
#WSGI_TEMPLATE             = template('application.wsgi')
SETTINGS_TEMPLATE         = template('settings/settings.py')
LOCAL_SETTINGS_TEMPLATE   = template('settings/local_settings.py')
DEV_SETTINGS_TEMPLATE     = template('settings/dev.py')
DEFAULT_SETTINGS_TEMPLATE = template('settings/default.py')
URLS_TEMPLATE             = template('urls.py')


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = Egg(buildout, options['recipe'], options)

        options.setdefault('bin-directory',
            buildout['buildout']['bin-directory'])
        options.setdefault('project', 'project')
        options.setdefault('settings', 'settings')
        options.setdefault('create_project', 'true')
        options.setdefault('urlconf', options['project'] + '.urls')
        options.setdefault('media_root',
            "os.path.join(os.path.dirname(__file__), 'media')")
        options.setdefault('extra-paths',
            buildout["buildout"].get('extra-paths', ''))
        options.setdefault('script-name',  name)

    def install(self):
        base_dir = self.buildout['buildout']['directory']
        project_dir = os.path.join(base_dir, self.options['project'])

        extra_paths = [base_dir]
        extra_paths.extend([p.replace('/', os.path.sep) for p in
            self.options['extra-paths'].splitlines() if p.strip()])

        requirements, ws = self.egg.working_set(['djangodukerecipe'])

        scripts = []

        # Create the Django management script
        scripts.extend(self.create_manage_script(extra_paths, ws))

        # Make the wsgi and fastcgi scripts if enabled
       #scripts.extend(self.make_scripts(extra_paths, ws))

        if self.options['create_project'] == 'true':
            if not os.path.exists(project_dir):
                self.create_project(project_dir)
            else:
                logger.info('Skipping creating of project: %(project)s '
                    'since it exists' % self.options)

        return scripts

    def create_manage_script(self, extra_paths, ws):
        return zc.buildout.easy_install.scripts(
            [(self.options['script-name'], 'djangodukerecipe.manage', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            extra_paths = extra_paths, arguments='"%s"' % self.options['settings'])

    def create_project(self, project_dir):
        """
        Django 1.4 project structure

        + project-root-folder/
          - manage.py (skipped)
          + project
            - __init__.py
            - settings.py
            - urls.py 
            - wsgi.py (skipped)

        Django duke final project structure

        + project-root-folder/
          - setup.py
          - bootstrap.py
          - buildout.cfg
          + project
            - __init__.py
            - settings.py
            - local_settings.py
            - urls.py 
            + conf/
              - default.py
              - dev.py
        """
        p = "',\n    '".join(self.buildout['python']['extra-paths'].split('\n'))
        template_vars = {
            'secret': self.generate_secret(),
            'pythonpaths': "'%s'," % p
        }
        template_vars.update(self.options)

        # Create project directory and __init__.py 
        os.makedirs(project_dir)
        open(os.path.join(project_dir, '__init__.py'), 'w').close()

        # Create conf directories
        os.makedirs(os.path.join(project_dir, 'conf/'))
        open(os.path.join(project_dir, 'conf/__init__.py'), 'w').close()

        os.makedirs(os.path.join(project_dir, 'conf/settings/'))
        open(os.path.join(project_dir, 'conf/settings/__init__.py'), 'w').close()
        
        # Create the wsgi application
        self.create_file(os.path.join(project_dir, 'wsgi.py'),
            WSGI_TEMPLATE, template_vars)

        # Create root urls.py
        self.create_file(os.path.join(project_dir, 'urls.py'),
            URLS_TEMPLATE, template_vars)

        # Create settings entry point
        self.create_file(os.path.join(project_dir, 'settings.py'),
            SETTINGS_TEMPLATE, template_vars)

        # Create local settings
        self.create_file(os.path.join(project_dir, 'local_settings.py.example'),
            LOCAL_SETTINGS_TEMPLATE, template_vars)

        # Create default (base) settings
        self.create_file(os.path.join(project_dir, 'conf/settings/default.py'),
            DEFAULT_SETTINGS_TEMPLATE, template_vars)

        # Create default (base) development settings
        self.create_file(os.path.join(project_dir, 'conf/settings/dev.py'),
            DEV_SETTINGS_TEMPLATE, template_vars)

        # Create the media directory
        os.mkdir(os.path.join(project_dir, 'media'))
        os.mkdir(os.path.join(project_dir, 'media/uploads/'))


   #def make_scripts(self, extra_paths, ws):
   #    # The scripts function uses a script_template variable hardcoded
   #    # in Buildout to generate the script file. Since the wsgi file
   #    # needs to create a callable application function rather than call
   #    # a script, monkeypatch the script template here.
   #    _script_template = zc.buildout.easy_install.script_template

   #    zc.buildout.easy_install.script_template = \
   #        zc.buildout.easy_install.script_header + WSGI_TEMPLATE

   #    generated = zc.buildout.easy_install.scripts(
   #        [('%s.wsgi' % self.options['script-name'],
   #            'djangodukerecipe.wsgi', 'main')],
   #        ws, self.options['executable'], 
   #        self.options['bin-directory'], extra_paths = extra_paths,
   #        #arguments= "'%s.%s'" % (self.options["project"],
   #        #    self.options['settings'])
   #        arguments = "'%s'" % self.options.get("settings", self.options.get('project') + ".settings")
   #    )

   #    zc.buildout.easy_install.script_template = _script_template

   #    return generated

    def update(self):
        self.install()

    def command(self, cmd, **kwargs):
        output = subprocess.PIPE
        if self.buildout['buildout'].get('verbosity'):
            output = None
        command = subprocess.Popen(cmd, shell=True, stdout=output, **kwargs)
        return command.wait()

    def create_file(self, f, template, options):
        if os.path.exists(f):
            return

        f = open(f, 'w')
        f.write(template % options)
        f.close()

    def generate_secret(self):
        # TODO: Really ? Check how django generate it's secret.
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([choice(chars) for i in range(50)])
