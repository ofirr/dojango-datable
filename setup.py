# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

from datable import version

import os

setup(
    name='dojango-datable',
    version=version,
    author=u'Michał Pasternak - FHU Kagami',
    author_email='michal.dtz@gmail.com',
    url='http://code.google.com/p/dojango-datable/',
    description='Dynamic Dojo DataGrids for Django',
    license='MIT',
    packages=find_packages(exclude=['test_project']),
    zip_safe=False,
    package_data={'datable': [
        'templates/*/*/*.html',
        'templates/*/*/*/*.html',
        'locale/*/LC_MESSAGES/django.mo',
        'locale/*/LC_MESSAGES/django.po',
    ]},
    include_package_data=True,
    install_requires=[
        'dojango', 'xlwt', 'ludibrio', 'iso8601', 'pytz', 'xlrd']
)
