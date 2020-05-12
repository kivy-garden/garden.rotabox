#!/usr/bin/env python


from setuptools import setup
from setuptools import Extension

setup(ext_modules=[Extension("cybounds", ["cybounds.c"])])

### In case of a modified 'cybounds.pyx.', use this 'setup' instead.#
# from Cython.Build import cythonize#
# setup(name='cybounds', ext_modules=cythonize('cybounds.pyx', annotate=True))
###

# COMMANDS
#
# in linux/mac:
# $ python setup.py build_ext --inplace
#
# in windows:
# $ python setup.py build_ext -i --compiler=msvc
