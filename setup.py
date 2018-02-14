#!/usr/bin/env python

from setuptools import setup, find_packages

import tt

install_requires = [
    'dateparser',
    'iso8601',
    'pandas',
    'SQLALchemy',
    'SQLAlchemy-Utc',
    'tabulate',
]

setup_requires = [
    'pytest-runner',
]

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-mock',
]

console_scripts = [
    'tt = tt.cli:main',
]

setup(name='timetrack2',
      version=tt.__VERSION__,
      description='Simple time tracker',
      author=tt.__AUTHOR__,
      author_email=tt.__AUTHOR_EMAIL__,
      packages=find_packages(),
      include_package_data=True,
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require,
      entry_points={
          'console_scripts': console_scripts,
      })

