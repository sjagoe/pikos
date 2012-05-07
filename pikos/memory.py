from __future__ import absolute_import
import inspect
import os
import psutil
import sys

from pikos.abstract_monitors import AbstractMonitor


__all__ = ['FunctionMemoryProfiler']


class AbstractMemoryProfiler(AbstractMonitor):
    """ Base class to set up common requirements for all MemoryProfilers
    """

    _fields = None

    def __init__(self, function, recorder):
        """ Initialize the profiler class

        Parameters
        ----------
        function : callable
            The callable to profile

        recorder :
            An instance of pikos.recorders.AbstractRecorder
        """
        super(AbstractMemoryProfiler, self).__init__(function, recorder)
        self._process = None

    def setup(self):
        """ Set up requirements for memory profiling
        """
        self._process = psutil.Process(os.getpid())
        self._recorder.prepare(self._fields)

    def teardown(self):
        """ Clean up after profiling is complete
        """
        self._process = None
        self._recorder.finalize()


class FunctionMemoryProfiler(AbstractMemoryProfiler):
    """ A concrete class for collecting memory information on function
    calls and returns
    """

    _fields = ['Type', 'Filename', 'LineNo', 'Function', 'RSS', 'VMS']

    def enable(self):
        """ Set up for profiling function calls
        """
        sys.setprofile(self.on_function_event)

    def disable(self):
        """ Remove function call profiler
        """
        sys.settrace(None)

    def on_function_event(self, frame, event, arg):
        """ Collect profiling information and pass it to the recorder
        """
        usage = self._process.get_memory_info()
        filename, lineno, function, _, _ = inspect.getframeinfo(
            frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = dict(zip(self._fields, (event, filename, lineno, function,
                                         usage.rss, usage.vms)))
        self._recorder.record(self._fields, record)
