#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

requirements = []
test_requirements = []

setup(
    author="Levi Malott",
    author_email='levi@malott.co',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    description="WindNinja server implementation",
    entry_points={
        'console_scripts': [
            'windninja_server=windninja_server.cli:main',
        ],
    },
    install_requires=requirements,
    license="",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='windninja_server',
    name='windninja_server',
    packages=find_packages(include=['windninja_server']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/firelab/windninja-mobile',
    version='1.1.0',
    zip_safe=False,
)
