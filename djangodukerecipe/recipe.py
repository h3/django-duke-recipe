import logging
import os
import subprocess

from zc.recipe.egg import Egg
import zc.buildout.easy_install

logger = logging.getLogger(__name__)


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = Egg(buildout, options['recipe'], options)

        options.setdefault('bin-directory',
            buildout['buildout']['bin-directory'])

        options.setdefault('project', 'project')
        options.setdefault('settings', 'settings')
        options.setdefault('create-project', 'true')
        options.setdefault('url-conf', options['project'] + '.urls')
        options.setdefault('extra-paths',
            buildout["buildout"].get('extra-paths', ''))
        options.setdefault('script-name',  name)

    def install(self):
        scripts     = []
        base_dir    = self.buildout['buildout']['directory']
        extra_paths = [base_dir]

        extra_paths.extend([p.replace('/', os.path.sep) for p in
            self.options['extra-paths'].splitlines() if p.strip()])

        for p in os.listdir(self.buildout['buildout']['eggs-directory']):
            if p.endswith('.egg'):
                extra_paths.append(os.path.join(base_dir, '.duke/eggs/%s/' % p))

        requirements, ws = self.egg.working_set(['djangodukerecipe'])

        # Create the Django management script
        scripts.extend(self.create_manage_script(extra_paths, ws))

        # Make the wsgi and fastcgi scripts if enabled
        #scripts.extend(self.make_scripts(extra_paths, ws))

        if self.options['create-project'] == 'true':
            self.create_project()

        return scripts

    def create_manage_script(self, extra_paths, ws):
        return zc.buildout.easy_install.scripts(
            [(self.options['script-name'], 'djangodukerecipe.manage', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            extra_paths = extra_paths, arguments='"%s"' % self.options['settings'])

    def create_project(self):
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
        base_dir    = self.buildout['buildout']['directory']
        project_dir = os.path.join(base_dir, self.options['project'])
        bin_path    = os.path.join(base_dir, '.duke/bin/')

        if os.path.exists(project_dir):
            logger.info('Skipping creating of project: %(project)s '
                'since it exists' % self.options)
        else:
           #p = "',\n    '".join(self.buildout['python']['extra-paths'].split('\n'))

            logger.info('Creating project: %s ' % self.options['project'])
            logger.info(self.options['extra-paths'])

            self.command('%(django)s startproject %(options)s %(project)s %(dest)s' % {
                'django': os.path.join(bin_path, 'django'), 
                'project': self.options['project'],
                'options': '--template=%s --extension=py,rst' % self.options['template'],
                'dest': base_dir,
            })


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
        logger.info('Executing %s ' % cmd)
        output = subprocess.PIPE
        if self.buildout['buildout'].get('verbosity'):
            output = None
        command = subprocess.Popen(cmd, shell=True, stdout=output, **kwargs)
        return command.wait()
