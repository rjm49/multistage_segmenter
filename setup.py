#!/usr/bin/env python
from setuptools import setup

setup(name='mseg',
      version='0.1',
      author='russell moore',
      author_email='russell@russellmoo.re',
      py_modules=['commmon'],
      packages=['slm','pm'],
      scripts=['scripts/rbf_svm.py'],
)
