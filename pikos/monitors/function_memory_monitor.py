from __future__ import absolute_import
import inspect
import os
import psutil
from collections import namedtuple
from pikos._internal.profile_functions import ProfileFunctions
from pikos.recorders.abstract_record_formater import AbstractRecordFormater
from pikos._internal.keep_track import KeepTrack

__all__ = [
    'FunctionMemoryMonitor',
    'FunctionMemoryRecord',
    'FunctionMemoryRecordFormater'
]

FUNCTION_MEMORY_RECORD = ('index', 'type', 'function', 'RSS', 'VMS', 'lineNo',
                          'filename')
FUNCTION_MEMORY_RECORD_TEMPLATE = ('{:<8} {:<11} {:<8} {:<8} {:<30} {:<5} {}'
                                   '{newline}')

FunctionMemoryRecord = namedtuple('FunctionMemoryRecord',
                                  FUNCTION_MEMORY_RECORD)

# we might need a factory function for this
class FunctionMemoryRecordFormater(AbstractRecordFormater):

    def header(self, record):
        return FUNCTION_MEMORY_RECORD_TEMPLATE.format(*record._fields,
                                                      newline=os.linesep)

    def line(self, record):
        return FUNCTION_MEMORY_RECORD_TEMPLATE.format(*record,
                                                      newline=os.linesep)

class FunctionMemoryMonitor(object):
    """ Record process memory on python function events. """

    _fields = FunctionMemoryRecord._fields

    def __init__(self, recorder):
        """ Initialize the function memory monitor class.

        Parameters
        ----------
        recorder : pikos.recorders.AbstractRecorder
            An instance of a Pikos recorder to handle the values to be logged
        """
        self._recorder = recorder
        self._profiler = ProfileFunctions()
        self._index = 0
        self._call_tracker = KeepTrack()
        self._process = None

    def __enter__(self):
        if self._call_tracker('ping'):
            self._process = psutil.Process(os.getpid())
            self._recorder.prepare(FunctionMemoryRecord)
            self._profiler.set(self.on_function_event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._call_tracker('pong'):
            self._profiler.unset()
            self._recorder.finalize()

    def on_function_event(self, frame, event, arg):
        usage = self._process.get_memory_info()
        filename, lineno, function, _, _ = \
            inspect.getframeinfo(frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = FunctionMemoryRecord(self._index, event, function, usage.rss,
                                      usage.vms, lineno, filename)
        self._recorder.record(record)
        self._index += 1
