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
from pikos._internal.keep_track import KeepTrack


class FocusedFunctionMonitor(FunctionMonitor):
    """ Record python function events in a `focused` way.

    Overrides FunctionMonitor to only record events when the interpreter is
    working inside the functions that are provided in the `functions`
    attribute.

    Public
    ------
    functions : FunctionSet
        A set of function or method objects inside which recording will
        take place.

    Private
    -------
    _code_trackers : dictionary
        A dictionary of KeepTrack instances associated with the code object
        of each function in `functions`. It is used to keep track and check
        that we are inside the execution of one these functions when we
        record data.

    """

    def __init__(self, recorder, functions=()):
        """ Initialize the monitoring class.

        Parameters
        ----------
        recorder : object
            A subclass of :class:`~pikos.recorders.AbstractRecorder` or a
            class that implements the same interface to handle the values
            to be logged.

        functions : list
            A list of function or method objects inside which recording will
            take place.

        """
        super(FocusedFunctionMonitor, self).__init__(recorder)
        self.functions = FunctionSet(functions)
        self._code_trackers = {}

    def on_function_event(self, frame, event, arg):
        """ Record the current function event only when we are inside one
        of the provided functions.

        """
        code = frame.f_code
        if code in self.functions:
            tracker = self._code_trackers.setdefault(code, KeepTrack())
            if event == 'call':
                tracker('ping')
            else:
                tracker('pong')
            self.on_focused_function_event(frame, event, arg)
            if not tracker:
                del self._code_trackers[code]
        elif any(self._code_trackers.viewvalues()):
            self.on_focused_function_event(frame, event, arg)

    on_focused_function_event = FunctionMonitor.on_function_event