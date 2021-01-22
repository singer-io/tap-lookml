#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-lookml',
      version='0.0.2',
      description='Singer.io tap for extracting metadata from LookML files with the GitHub API',
      author='jeff.huth@bytecode.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_lookml'],
      install_requires=[
          'lkml==0.2.1',
          'backoff==1.8.0',
          'requests==2.22.0',
          'singer-python==5.8.1'
      ],
      extras_require={
        'dev': [
            'pylint',
            'ipdb'
        ]
      },
      entry_points='''
          [console_scripts]
          tap-lookml=tap_lookml:main
      ''',
      packages=find_packages(),
      package_data={
          'tap_lookml': [
              'schemas/*.json'
          ]
      })
