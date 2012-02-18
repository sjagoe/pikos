# -*- coding: UTF-8 -*-
#------------------------------------------------------------------------------
#  file: setup.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from setuptools import setup, find_packages

setup(name='pikos',
    version='0.1a',
    author='Enthought, Inc',
    author_email='ioannist@enthought.com',
    description='Enthought profiling tools',
    requires=['psutil'],
    install_requires=['distribute'],
    packages=find_packages())
