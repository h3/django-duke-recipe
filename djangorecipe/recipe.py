from random import choice
import os
import subprocess
import urllib2
import shutil
import logging
import re

from zc.buildout import UserError
import zc.recipe.egg
import setuptools

script_template = {
    'wsgi': """

%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
  ]
%(initialization)s
import %(module_name)s

application = %(module_name)s.%(attrs)s(%(arguments)s)
""",
    'fcgi': """

%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
  ]
%(initialization)s
import %(module_name)s

%(module_name)s.%(attrs)s(%(arguments)s)
"""
}


SETTINGS_TEMPLATE = """
import os

MANAGERS = ADMINS = ()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'project.db',
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

ADMIN_MEDIA_PREFIX = '/admin_media/'
MEDIA_ROOT = %(media_root)s
MEDIA_URL = '/media/'

SECRET_KEY = '%(secret)s'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = '%(urlconf)s'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)
"""

URLS_TEMPLATE = """
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
      {'document_root': settings.MEDIA_ROOT}),
)
"""

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.log = logging.getLogger(name)
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)

        self.buildout, self.name, self.options = buildout, name, options
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], name)
        options['bin-directory'] = buildout['buildout']['bin-directory']

        options.setdefault('project', 'project')
        options.setdefault('settings', 'settings')

        options.setdefault('urlconf', options['project'] + '.urls')
        options.setdefault('media_root',
            "os.path.join(os.path.dirname(__file__), 'media')")
        # Set this so the rest of the recipe can expect the values to be
        # there. We need to make sure that both pythonpath and extra-paths are
        # set for BBB.
        if 'extra-paths' in options:
            options['pythonpath'] = options['extra-paths']
        else:
            options.setdefault('extra-paths', options.get('pythonpath', ''))

        # mod_wsgi support script
        options.setdefault('wsgi', 'false')
        options.setdefault('fcgi', 'false')
        options.setdefault('logfile', '')

    def install(self):
        location = self.options['location']
        base_dir = self.buildout['buildout']['directory']

        project_dir = os.path.join(base_dir, self.options['project'])

        version = self.options['version']
        # Remove a pre-existing installation if it is there
        if os.path.exists(location):
            shutil.rmtree(location)

        self.install_git_version(version, location)

        extra_paths = [os.path.join(location), base_dir]

        # Add libraries found by a site .pth files to our extra-paths.
        if 'pth-files' in self.options:
            import site
            for pth_file in self.options['pth-files'].splitlines():
                pth_libs = site.addsitedir(pth_file, set())
                if not pth_libs:
                    self.log.warning(
                        "No site *.pth libraries found for pth_file=%s" % (
                         pth_file,))
                else:
                    self.log.info("Adding *.pth libraries=%s" % pth_libs)
                    self.options['extra-paths'] += '\n' + '\n'.join(pth_libs)

        pythonpath = [p.replace('/', os.path.sep) for p in
                      self.options['extra-paths'].splitlines() if p.strip()]

        extra_paths.extend(pythonpath)
        requirements, ws = self.egg.working_set(['djangorecipe'])

        # Create the Django management script
        self.create_manage_script(extra_paths, ws)

        # Create the test runner
        self.create_test_runner(extra_paths, ws)

        # Make the wsgi and fastcgi scripts if enabled
        self.make_scripts(extra_paths, ws)

        # Create default settings if we haven't got a project
        # egg specified, and if it doesn't already exist
        if not self.options.get('projectegg'):
            if not os.path.exists(project_dir):
                self.create_project(project_dir)
            else:
                self.log.info(
                    'Skipping creating of project: %(project)s since '
                    'it exists' % self.options)

        return location

    def install_git_version(self, version, location):
        git_url = self.git_to_url()

        if os.path.exists(location):
            self.git_update(location)
        else:
            self.log.info("Checking out Django from git: %s" % git_url)
            cmd = 'git clone %s %s' % (git_url, location)
            self.log.info("Cloning with: %s" % cmd)
            self.command(cmd)

    def git_to_url(self):
        return self.options.get("repository",
            "git://github.com/django/django.git")

    def git_update(self, location):
        orig_cwd = os.getcwd()
        os.chdir(location)
        cmd = "git pull origin"
        if not self.buildout['buildout'].get('verbosity'):
            cmd += ' -q'
        self.command(cmd)
        os.chdir(orig_cwd)

    def create_manage_script(self, extra_paths, ws):
        project = self.options.get('projectegg', self.options['project'])
        zc.buildout.easy_install.scripts(
            [(self.options.get('control-script', self.name),
              'djangorecipe.manage', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            extra_paths = extra_paths,
            arguments= "'%s.%s'" % (project, self.options['settings']))

    def create_test_runner(self, extra_paths, working_set):
        apps = self.options.get('test', '').split()
        # Only create the testrunner if the user requests it
        if apps:
            zc.buildout.easy_install.scripts(
                [(self.options.get('testrunner', 'test'),
                  'djangorecipe.test', 'main')],
                working_set, self.options['executable'],
                self.options['bin-directory'],
                extra_paths = extra_paths,
                arguments= "'%s.%s', %s" % (
                    self.options['project'],
                    self.options['settings'],
                    ', '.join(["'%s'" % app for app in apps])))

    def create_project(self, project_dir):
        os.makedirs(project_dir)

        template_vars = {'secret': self.generate_secret()}
        template_vars.update(self.options)

        self.create_file(os.path.join(project_dir, 'urls.py'),
            URLS_TEMPLATE, template_vars)

        self.create_file(os.path.join(project_dir, 'settings.py'),
            SETTINGS_TEMPLATE, template_vars)

        # Create the media and templates directories for our project
        os.mkdir(os.path.join(project_dir, 'media'))
        os.mkdir(os.path.join(project_dir, 'templates'))

        # Make the settings dir a Python package so that Django
        # can load the settings from it. It will act like the
        # project dir.
        open(os.path.join(project_dir, '__init__.py'), 'w').close()

    def make_scripts(self, extra_paths, ws):
        _script_template = zc.buildout.easy_install.script_template
        for protocol in ('wsgi', 'fcgi'):
            zc.buildout.easy_install.script_template = \
                zc.buildout.easy_install.script_header + \
                    script_template[protocol]
            if self.options.get(protocol, '').lower() == 'true':
                project = self.options.get('projectegg',
                                           self.options['project'])
                zc.buildout.easy_install.scripts(
                    [('%s.%s' % (self.options.get('control-script', self.name),
                                protocol),
                      'djangorecipe.%s' % protocol, 'main')],
                    ws,
                    self.options['executable'], 
                    self.options['bin-directory'],extra_paths = extra_paths,
                    arguments= "'%s.%s', logfile='%s'" % (
                        project, self.options['settings'],
                        self.options.get('logfile')))
        zc.buildout.easy_install.script_template = _script_template

    def update(self):
        newest = self.buildout['buildout'].get('newest') != 'false'

    def command(self, cmd, **kwargs):
        output = subprocess.PIPE
        if self.buildout['buildout'].get('verbosity'):
            output = None
        command = subprocess.Popen(
            cmd, shell=True, stdout=output, **kwargs)
        return command.wait()

    def create_file(self, file, template, options):
        if os.path.exists(file):
            return

        f = open(file, 'w')
        f.write(template % options)
        f.close()

    def generate_secret(self):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return ''.join([choice(chars) for i in range(50)])
