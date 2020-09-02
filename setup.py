#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
import re


def find_version():
    return re.search(r"^__version__ = '(.*)'$",
                     open('mys/version.py', 'r').read(),
                     re.MULTILINE).group(1)


setup(name='mys',
      version=find_version(),
      description='Strongly typed Python to C++ transpiler.',
      long_description=open('README.rst', 'r').read(),
      author='Erik Moqvist',
      author_email='erik.moqvist@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ],
      python_requires='>=3.6',
      keywords=['programming-language'],
      url='https://github.com/eerimoq/mys',
      packages=find_packages(exclude=['tests']),
      install_requires=[
          'ansicolors',
          'pygments',
          'toml',
          'yaspin'
      ],
      test_suite="tests",
      include_package_data=True,
      entry_points = {
          'console_scripts': ['mys=mys.cli:main']
      })
