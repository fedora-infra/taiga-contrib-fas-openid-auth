#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

setup(
    name='taiga-contrib-fas-openid-auth',
    version='0.3',
    description="The Taiga plugin for FAS authentication",
    long_description="",
    keywords='taiga, fas, openid, fedora, auth, plugin',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='https://github.com/fedora-infra/taiga-contrib-fas-openid-auth',
    license='AGPL',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'django',
        'python3-openid',
        'python-openid-cla',
        'python-openid-teams',
    ],
    classifiers=[
        "Programming Language :: Python",
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
