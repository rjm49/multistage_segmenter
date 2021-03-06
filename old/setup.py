#!/usr/bin/env python
from setuptools import setup, find_packages
import os

setup(name='mseg',
      version='0.16',
      author='russell moore',
      author_email='russell@russellmoo.re',
      packages=find_packages(exclude=('tests','docs')),
      scripts=['scripts/train_pm.py','scripts/main_run.py','scripts/create_models.py'],
)

os.system('rm -rf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')