#!/usr/bin/env python


from setuptools import setup
from setuptools import Extension

setup(ext_modules=[Extension("cybounds", ["cybounds.c"])])


# COMMANDS
#
# in linux/mac:
# $ python setup.py build_ext --inplace
#
# in windows:
# $ python setup.py build_ext -i --compiler=msvc
