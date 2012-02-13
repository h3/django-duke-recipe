Overview
========

A django recipe modified for django-duke.

Based on Preston Timmons' fork of `djangorecipe`:
http://github.com/prestontimmons/thechristmaspig

Example Recipe
==============

::

    [buildout]
    parts = python django django-project
    eggs =
    extra-paths =
        ${buildout:directory}
        ${buildout:directory}/parts/django/

    [python]
    recipe = zc.recipe.egg
    interpreter = python
    eggs = ${buildout:eggs}
    extra-paths = ${buildout:extra-paths}

    [django]
    recipe = zerokspot.recipe.git
    repository = git://github.com/django/django.git

    [django-project]
    recipe = djangodukerecipe
    project = example
    script-name = django
    eggs = ${buildout:eggs}


Supported options
=================

The recipe supports the following options.

``project``
    The name of the project directory to use or create.

``settings``
    The name of the settings file for the project. Defaults to ``settings``.

``extra-paths``
    Paths to extend the default Python path for the generated scripts.
    Defaults to the extra-paths parameter of the [buildout] configuration.

``script-name``
    The name of the scripts created in the bin folder. This script is the
    equivalent of the ``manage.py`` Django normally creates. By default it
    uses the name of the section (the part between the ``[ ]``).

``urlconf``
    You can set this to a specific url conf. It will use the
    ``project.urls`` where project is set by the ``project`` option.


Sandbox Installation
====================

Use the following commands to run a demo of this package.

::

    $ git clone git://github.com/h3/djangodukerecipe.git
    $ cd djangodukerecipe
    $ python bootstrap.py
    $ bin/buildout -v
    $ bin/django test



.. _`djangorecipe`: http://pypi.python.org/pypi/djangorecipe
