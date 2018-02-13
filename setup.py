#!/usr/bin/env python

from setuptools import setup, find_packages

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
    'python-coveralls',
    'pytest',
    'pytest-cov',
    'pytest-mock',
]

console_scripts = [
    'tt = tt.cli:main',
]

setup(name='timetrack2',
      version='1.0.0',
      description='Simple time tracker',
      author='Anthony Oteri',
      author_email='anthony.oteri@gmail.com',
      packages=find_packages(),
      include_package_data=True,
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require,
      entry_points={
          'console_scripts': console_scripts,
      })

