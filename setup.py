#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = [
    'dateparser',
    'humanfriendly',
    'SQLALchemy',
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
      install_requires=install_requires,
      entry_points={
          'console_scripts': console_scripts,
      })

