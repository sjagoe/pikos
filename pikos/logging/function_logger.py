from __future__ import absolute_import
import inspect

from collections import namedtuple
from pikos._profile_functions import ProfileFunctions

__all__ = [
    'FunctionLogger',
    'FunctionRecord',
]

FunctionRecord = namedtuple('FunctionRecord',
                            ['type', 'filename', 'lineNo', 'function'])


class FunctionLogger(object):

    _fields = FunctionRecord._fields

    def __init__(self, recorder):
        """ Initialize the logger class.

        Parameters
        ----------
        recorder : pikos.recorders.AbstractRecorder
            An instance of a Pikos recorder to handle the values to be logged
        """
        self._recorder = recorder
        self._profiler = ProfileFunctions()

    def __enter__(self):
        self._recorder.prepare(self._fields)
        self._profiler.set(self.on_function_event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._profiler.unset()
        self._recorder.finalize()

    def on_function_event(self, frame, event, arg):
        filename, lineno, function, _, _ = \
            inspect.getframeinfo(frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = FunctionRecord(event, filename, lineno, function)
        self._recorder.record(record)


