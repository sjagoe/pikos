# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
#  file: setup.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from setuptools import setup, find_packages, Extension, Feature

real_time_lsprof = Feature(
    'optional real time lsrof using zmq',
    standard=False,
    ext_modules=[
        Extension(
            'pikos._internal._lsprof_rt',
            sources=['pikos/_internal/_lsprof_rt.c',
                     'pikos/_internal/rotatingtree.c'])]
    )

setup(
    name='pikos',
    version='0.1a',
    author='Enthought Inc',
    author_email='info@enthought.com',
    description='Enthought monitoring and profiling tools',
    requires=['psutil'],
    install_requires=['distribute'],
    packages=find_packages(),
    entry_points=dict(
        console_scripts=['pikos-run = pikos.runner:main']),
    features={'real-time-lsprof': real_time_lsprof})
