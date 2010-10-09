import os

from setuptools import setup, find_packages

version = '0.19.2'

setup(
    name='djangorecipe',
    version=version,
    description="Buildout recipe for Django",
    long_description=open("README.rst").read(),
    classifiers=[
      'Framework :: Buildout',
      'Framework :: Django',
      'Topic :: Software Development :: Build Tools',
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: BSD License',
      ],
    package_dir={'': 'djangorecipe'},
    packages=find_packages('djangorecipe'),
    keywords='',
    author='Jeroen Vloothuis',
    author_email='jeroen.vloothuis@xs4all.nl',
    url='https://launchpad.net/djangorecipe',
    license='BSD',
    zip_safe=False,
    install_requires=[
      'zc.buildout',
      'zc.recipe.egg',
    ],
    entry_points="""
    # -*- Entry points: -*-
    [zc.buildout]
    default = recipe:Recipe
    """,
)
