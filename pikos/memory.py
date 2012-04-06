from __future__ import absolute_import
import csv
import datetime
import gc
import inspect
import os
import psutil
import sys

from pikos.abstract_monitors import AbstractMonitor


__all__ = ['FunctionMemoryProfiler']


class AbstractMemoryProfiler(AbstractMonitor):

    _fields = None

    def __init__(self, function, recorder):
        ''' Initialize the profiler class

        Parameters
        ----------
        function : callable
            The callable to profile

        recorder :
            An instance of pikos.recorders.AbstractRecorder
        '''
        super(AbstractMemoryProfiler, self).__init__(function)
        self._recorder = recorder
        self._process = None

    def setup(self):
        self._process = psutil.Process(os.getpid())
        self._recorder.prepare(self._fields)

    def teardown(self):
        self._process = None
        self._recorder.finalize()


class FunctionMemoryProfiler(AbstractMemoryProfiler):

    _fields = ['Type', 'Filename', 'LineNo', 'Function', 'RSS', 'VMS']

    def setup(self):
        super(FunctionMemoryProfiler, self).setup()
        sys.setprofile(self.on_function_event)

    def teardown(self):
        sys.settrace(None)
        super(FunctionMemoryProfiler, self).teardown()

    def on_function_event(self, frame, event, arg):
        usage = self._process.get_memory_info()
        filename, lineno, function, _, _ = inspect.getframeinfo(
            frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = dict(zip(self._fields, (event, filename, lineno, function,
                                         usage.rss, usage.vms)))
        self._recorder.record(self._fields, record)
