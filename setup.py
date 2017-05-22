#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import setuptools.command.install
import setuptools.command.develop
import setuptools.command.sdist
from distutils.core import Command
from setuptools import setup, find_packages


# Utility function to read the README file. Also support json content
def read_file(fname, content_type=None):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    p = os.path.join(dir_path, fname)
    with open(p) as f:
        if content_type in ('json',):
            data = json.load(f)
        else:
            data = f.read()
    return data


def read_version():
    d = read_file('package.json', 'json')
    return d['version']


VERSION = read_version()
DESCRIPTION = 'OMERO forms app for enhanced metadata input and provenance'
AUTHOR = 'D.P.W. Russell'
LICENSE = 'AGPL-3.0'
HOMEPAGE = 'https://github.com/sorgerlab/OMERO.forms'


cmdclass = {}


class NpmInstall(Command):

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.spawn(['npm', 'install'])


cmdclass['npm_install'] = NpmInstall


class WebpackBuild(Command):

    sub_commands = [
        ('npm_install', None)
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.isdir('src'):
            return
        for command in self.get_sub_commands():
            self.run_command(command)
        self.spawn(['node_modules/webpack/bin/webpack.js', '-p'])


cmdclass['webpack_build'] = WebpackBuild


class Sdist(setuptools.command.sdist.sdist):

    def run(self):
        if os.path.isdir('src'):
            self.run_command('webpack_build')
        setuptools.command.sdist.sdist.run(self)


cmdclass['sdist'] = Sdist


class Install(setuptools.command.install.install):

    def run(self):
        if os.path.isdir('src'):
            self.run_command('webpack_build')
        setuptools.command.install.install.run(self)


cmdclass['install'] = Install


setup(
    name='omero-forms',
    packages=find_packages(exclude=['ez_setup']),
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_file('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: '
        'Application Frameworks',
        'Topic :: Text Processing :: Markup :: HTML'
    ],  # Get strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    author=AUTHOR,
    author_email='douglas_russell@hms.harvard.edu',
    license=LICENSE,
    url=HOMEPAGE,
    download_url='%s/archive/%s.tar.gz' % (HOMEPAGE, VERSION),
    keywords=['OMERO.web', 'forms', 'provenance', 'history'],
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
    cmdclass=cmdclass,
)
