from __future__ import absolute_import
import csv
import datetime
import gc
import inspect
import os
import psutil
import sys

from pikos.abstract_monitors import AbstractFunctionMonitor, AbstractTimeMonitor


__all__ = ['MemoryProfiler']


class AbstractMemoryProfiler(AbstractFunctionMonitor):

    _fields = None

    def __init__(self, function, output=None, disable_gc=False):
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
        self._disable_gc = disable_gc
        if output is None:
            date = datetime.datetime.now()
            self._output = '{0}-{1}.profile'.format(
                self.__class__.__name__, date.strftime('%Y-%m-%d_%H-%M'))
        else:
            self._output = output

        self._process = None
        self._output_fh = None
        self._writer = None

    def _write_result(self, row):
        if self._writer is None:
            raise RuntimeError('The profiler has not been started')
        self._writer.writerow(row)

    def setup(self):
        self._output_fh = open(self._output, 'wb', buffering=0)
        self._writer = csv.writer(self._output_fh)
        self._writer.writerow(self._fields)
        self._process = psutil.Process(os.getpid())
        if self._disable_gc:
            gc.disable()
        super(AbstractMemoryProfiler, self).setup()

    def teardown(self):
        super(AbstractMemoryProfiler, self).teardown()
        if self._disable_gc:
            gc.enable()
        self._process = None
        self._writer = None
        self._output_fh.close()

    def _get_memory_info(self):
        return self._process.get_memory_info()


class MemoryProfiler(AbstractMemoryProfiler):

    _fields = ['Type', 'Filename', 'LineNo', 'Function', 'RSS', 'VMS']

    def on_function_event(self, frame, event, arg):
        usage = self._get_memory_info()
        filename, lineno, function, _, _ = inspect.getframeinfo(
            frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = (event, filename, lineno, function, usage.rss, usage.vms)
        self._write_result(record)
