#!/usr/bin/env python

import re

from setuptools import setup
from setuptools import find_packages
from setuptools import Extension

from mys.version import __version__


with open('requirements.txt') as f:
    requirements = [line for line in f]


setup(name='mys',
      version=__version__,
      description='The Mys (/maɪs/) programming language.',
      long_description=open('README.rst', 'r').read(),
      author='Erik Moqvist',
      author_email='erik.moqvist@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ],
      python_requires='>=3.8',
      keywords=['programming-language'],
      url='https://github.com/eerimoq/mys',
      packages=find_packages(exclude=['tests']),
      install_requires=requirements,
      include_package_data=True,
      ext_modules=[
          Extension('mys.parser._ast',
                    sources=[
                        'mys/parser/Python-ast.c',
                        'mys/parser/asdl.c',
                        'mys/parser/parser.c',
                        'mys/parser/peg_api.c',
                        'mys/parser/token.c',
                        'mys/parser/tokenizer.c',
                        'mys/parser/pegen.c',
                        'mys/parser/string_parser.c'
                    ])
      ],
      entry_points={
          'console_scripts': ['mys=mys.cli:main']
      })
