from __future__ import absolute_import
import inspect
import os
import psutil
import sys

from collections import namedtuple
from pikos._profile_functions import ProfileFunctions


__all__ = [
    'FunctionMemoryProFiler',
    'FunctionMemoryRecord',
]

FunctionMemoryRecord = namedtuple('FunctionRecord',
                    ['Type', 'Filename', 'LineNo', 'Function', 'RSS', 'VMS'])

class FunctionMemoryProfiler(object):
    """ Base class to set up common requirements for all MemoryProfilers
    """

    _fields = FunctionMemoryRecord._fields

    def __init__(self, recorder):
        """ Initialize the function memory profiler class.

        Parameters
        ----------
        recorder : pikos.recorders.AbstractRecorder
            An instance of a Pikos recorder to handle the values to be logged
        """
        self._recorder = recorder
        self._profiler = ProfileFunctions()
        self._process = None

    def __enter__(self):
        """ Set up requirements for memory profiling
        """
        self._process = psutil.Process(os.getpid())
        self._recorder.prepare(self._fields)
        self._profiler.set(self.on_function_event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Clean up after profiling is complete
        """
        self._profiler.unset()
        self._recorder.finalize()
        self._process = None


    def on_function_event(self, frame, event, arg):
        """ Collect profiling information and pass it to the recorder
        """
        usage = self._process.get_memory_info()
        filename, lineno, function, _, _ = \
            inspect.getframeinfo(frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = FunctionMemoryRecord(event, filename, lineno, function,
                                      usage.rss, usage.vms)
        self._recorder.record(record)
