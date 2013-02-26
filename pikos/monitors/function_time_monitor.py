# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
#  Package: Pikos toolkit
#  File: monitors/function_monitor.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from __future__ import absolute_import
import os
import inspect
import timeit
from collections import namedtuple

from pikos._internal.profile_function_manager import ProfileFunctionManager
from pikos._internal.keep_track import KeepTrack
from pikos.monitors.monitor import Monitor

FUNCTION_TIME_RECORD = ('index', 'type', 'function', 'lineNo', 'time', 'filename')
FUNCTION_TIME_RECORD_TEMPLATE = '{:<8} {:<11} {:<30} {:<5} {.8f} {}{newline}'


class FunctionTimeRecord(namedtuple('FunctionTimeRecord', FUNCTION_TIME_RECORD)):

    __slots__ = ()

    @classmethod
    def header(cls):
        """ Return a formatted header line """
        return FUNCTION_TIME_RECORD_TEMPLATE.format(*cls._fields,
                                                    newline=os.linesep)

    def line(self):
        """ Return a formatted header line """
        return FUNCTION_TIME_RECORD_TEMPLATE.format(*self, newline=os.linesep)


class FunctionMonitor(Monitor):
    """ Record python function events.

    The class hooks on the setprofile function to receive function events and
    record them.

    Private
    -------
    _recorder : object
        A recorder object that implementes the
        :class:`~pikos.recorder.AbstractRecorder` interface.

    _profiler : object
        An instance of the
        :class:`~pikos._internal.profiler_functions.ProfilerFunctions` utility
        class that is used to set and unset the setprofile function as required
        by the monitor.

    _index : int
        The current zero based record index. Each function event will increase
        the index by one.

    _call_tracker : object
        An instance of the :class:`~pikos._internal.keep_track` utility class
        to keep track of recursive calls to the monitor's :meth:`__enter__` and
        :meth:`__exit__` methods.

    """

    def __init__(self, recorder):
        """ Initialize the monitoring class.

        Parameters
        ----------
        recorder : object
            A subclass of :class:`~pikos.recorders.AbstractRecorder` or a class
            that implements the same interface to handle the values to be
            logged.

        """
        self._recorder = recorder
        self._profiler = ProfileFunctionManager()
        self._index = 0
        self._call_tracker = KeepTrack()
        self._time_dict = dict()
        #{(filename, lineno, function): [time_c0, time_r0, time_c1, time_r1]}

    def __enter__(self):
        """ Enter the monitor context.

        The first time the method is called (the context is entered) it will
        set the setprofile hooks and initialize the recorder.

        """
        if self._call_tracker('ping'):
            self._recorder.prepare(FunctionRecord)
            self._profiler.replace(self.on_function_event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Exit the monitor context.

        The last time the method is called (the context is exited) it will
        unset the setprofile hooks and finalize the recorder.

        """
        if self._call_tracker('pong'):
            self._profiler.recover()
            self._recorder.finalize()

    def on_function_event(self, frame, event, arg):
        """ Record the current function event.

        Called on function events, it will retrieve the necessary information
        from the `frame`, create a :class:`FunctionRecord` and send it to the
        recorder.

        """
        filename, lineno, function, _, _ = \
            inspect.getframeinfo(frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        if event.endswith('call'):
            self._time_dict[(filename, lineno, function)] = \
                timeit.default_timer()
        elif event.endswith('return'):
            delta_t = timeit.default_timer() - \
                self._time_dict[(filename, lineno, function)]
            record = FunctionTimeRecord(self._index, event,
                                        function, lineno, delta_t, filename)
            self._recorder.record(record)
            self._index += 1
