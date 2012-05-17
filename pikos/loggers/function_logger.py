from __future__ import absolute_import
import inspect

from collections import namedtuple
from pikos._internal.profile_functions import ProfileFunctions
from pikos.recorders.abstract_record_formater import AbstractRecordFormater

__all__ = [
    'FunctionLogger',
    'FunctionRecord',
    'FunctionRecordFormater'
]

FUNCTION_RECORD = ('index', 'type', 'function', 'lineNo', 'filename')
FUNCTION_RECORD_TEMPLATE = '{:<8} {:<11} {:<30} {:<5} {}{newline}'

FunctionRecord = namedtuple('FunctionRecord', FUNCTION_RECORD)

class FunctionRecordFormater(AbstractRecordFormater):

    def header(self, record):
        return FUNCTION_RECORD_TEMPLATE.format(*record._fields,
                                               newline=os.linesep)

    def line(self, record):
        return FUNCTION_RECORD_TEMPLATE.format(*record, newline=os.linesep)


class FunctionLogger(object):

    def __init__(self, recorder):
        """ Initialize the logger class.

        Parameters
        ----------
        recorder : pikos.recorders.AbstractRecorder
            An instance of a Pikos recorder to handle the values to be logged
        """
        self._recorder = recorder
        self._profiler = ProfileFunctions()
        self._index = 0
        self._run_counts = 0

    def __enter__(self):
        self._run_counts += 1
        if self._run_counts == 1:
            self._recorder.prepare(FunctionRecord)
            self._profiler.set(self.on_function_event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._run_counts -= 1
        if self._run_counts == 0:
            self._recorder.prepare(FunctionRecord)
            self._profiler.unset()

    def on_function_event(self, frame, event, arg):
        filename, lineno, function, _, _ = \
            inspect.getframeinfo(frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = FunctionRecord(self._index, event, function, lineno, filename)
        self._recorder.record(record)
        self._index += 1
