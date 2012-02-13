import os

from setuptools import setup, find_packages

 
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = ['zc.buildout', 'zc.recipe.egg']

setup(
    name='django-duke-recipe.git',
    version="0.1.0",
    description="Buildout recipe for Django. Sets up controls scripts and wsgi file.",
    long_description=read("README.rst"),
    url='https://github.com/h3/djangodukerecipe',
    license='BSD',
    author='Maxime Haineault',
    author_email='max@motion-m.ca',
    classifiers=[
        'Framework :: Buildout',
        'Framework :: Django',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
    ],
    packages=find_packages(exclude=['example', 'parts', 'eggs']),
    package_data={'djangodukerecipe': ['*.wsgi']},
    keywords='',
    zip_safe=False,
    install_requires=requirements,
    entry_points={'zc.buildout': ['default = djangodukerecipe.recipe:Recipe']},
)
