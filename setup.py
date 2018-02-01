#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'dateparser',
    'humanfriendly',
    'SQLALchemy',
]

setup_requires= [
    'pytest-runner',
]

tests_require = [
    'python-coveralls',
    'pytest',
    'pytest-cov',
]

console_scripts = [
    't2 = tt.cli:main',
]

setup(name='timetrack2',
      version='0.0.0',
      description='Project based time tracking',
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

