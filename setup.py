# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
#  file: setup.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from setuptools import setup, find_packages, Extension

extensions = [
    Extension(
        'pikos._internal._lsprof_rt',
        sources=[
            'pikos/_internal/_lsprof_rt.c',
            'pikos/_internal/rotatingtree.c',
            ],
        ),
    ]

setup(
    name='pikos',
    version='0.1a',
    author='Enthought, Inc',
    author_email='ioannist@enthought.com',
    description='Enthought profiling tools',
    requires=['psutil'],
    install_requires=['distribute'],
    packages=find_packages(),
    ext_modules=extensions,
    )
