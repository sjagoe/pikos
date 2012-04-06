from __future__ import absolute_import
import csv
import datetime
import gc
import inspect
import os
import psutil
import sys

from pikos.abstract_monitors import AbstractMonitor


__all__ = ['MemoryProfiler']


class AbstractMemoryProfiler(AbstractMonitor):

    _fields = None

    def __init__(self, function, recorder, disable_gc=False):
        ''' Initialize the profiler class

        Parameters
        ----------
        function : callable
            The callable to profile

        output : str
            The file in which to store profiling results

        disable_gc : bool
            Indicates that the profiling should run with the garbage
            collector disabled
        '''
        super(AbstractMemoryProfiler, self).__init__(function)
        self._recorder = recorder
        self._disable_gc = disable_gc
        self._process = None

    def setup(self):
        self._process = psutil.Process(os.getpid())
        if self._disable_gc:
            gc.disable()
        self._recorder.prepare(self._fields)

    def teardown(self):
        if self._disable_gc:
            gc.enable()
        self._process = None
        self._recorder.finalize()

    def _get_memory_info(self):
        return self._process.get_memory_info()


class MemoryProfiler(AbstractMemoryProfiler):

    _fields = ['Type', 'Filename', 'LineNo', 'Function', 'RSS', 'VMS']

    def setup(self):
        super(MemoryProfiler, self).setup()
        sys.setprofile(self.on_function_event)

    def teardown(self):
        sys.settrace(None)
        super(MemoryProfiler, self).teardown()

    def on_function_event(self, frame, event, arg):
        usage = self._get_memory_info()
        filename, lineno, function, _, _ = inspect.getframeinfo(
            frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = dict(zip(self._fields, (event, filename, lineno, function,
                                         usage.rss, usage.vms)))
        self._recorder.record(self._fields, record)
