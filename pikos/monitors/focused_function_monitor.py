# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
#  Package: Pikos toolkit
#  File: monitors/function_monitor.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from __future__ import absolute_import

from pikos._internal.function_set import FunctionSet
from pikos.monitors.function_monitor import FunctionMonitor


class FocusedFunctionMonitor(FunctionMonitor):
    """ Record python function events in a `focused` way.

    Overrides FunctionMonitor to only record events when the interpret is
    functioning inside the functions that are provided in the `functions`
    attribute.

    Public
    ------
    functions : list
        A list of function or method objects inside which recording will
        take place.

    """

    def __init__(self, recorder, functions=()):
        """ Initialize the monitoring class.

        Parameters
        ----------
        recorder : object
            A subclass of :class:`~pikos.recorders.AbstractRecorder` or a class
            that implements the same interface to handle the values to be
            logged.

        functions : list
            A list of function or method objects inside which recording will
            take place.

        """
        super(FocusedFunctionMonitor, self).__init__(recorder)
        self.functions = FunctionSet(functions)

    def on_function_event(self, frame, event, arg):
        """ Record the current function event only when we are inside one
        of the defined functions.

        """
        code = frame.f_code
        if code in self.functions:
            super(FocusedFunctionMonitor, self).on_function_event(frame, event,
                                                                  arg)

