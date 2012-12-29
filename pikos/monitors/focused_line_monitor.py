# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
#  Package: Pikos toolkit
#  File: monitors/line_monitor.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from pikos._internal.function_set import FunctionSet
from pikos.monitors.line_monitor import LineMonitor


class FocusedLineMonitor(LineMonitor):
    """ Record python line events in a `focused` way.

    Overrides LineMonitor to only record events when the interpreter is
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
        super(FocusedLineMonitor, self).__init__(recorder)
        self.functions = FunctionSet(functions)

    def on_line_event(self, frame, why, arg):
        """ Record the current function event only when we are inside one
        of the provided functions.

        """
        code = frame.f_code
        if code in self.functions:
            self.on_focused_line_event(frame, why, arg)
        return self.on_line_event

    on_focused_line_event = LineMonitor.on_line_event
