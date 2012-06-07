from __future__ import absolute_import
import inspect

from collections import namedtuple
from pikos._internal.profile_functions import ProfileFunctions
from pikos._internal.keep_track import KeepTrack
from pikos.recorders.abstract_record_formater import AbstractRecordFormater

__all__ = [
    'FunctionMonitor',
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


class FunctionMonitor(object):
    """ Record python function events. """

    def __init__(self, recorder):
        """ Initialize the monitoring class.

        Parameters
        ----------
        recorder : ~pikos.recorders.AbstractRecorder
            An instance of a Pikos recorder to handle the values to be logged
        """
        self._recorder = recorder
        self._profiler = ProfileFunctions()
        self._index = 0
        self._call_tracker = KeepTrack()

    def __enter__(self):
        if self._call_tracker('ping'):
            self._recorder.prepare(FunctionRecord)
            self._profiler.set(self.on_function_event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._call_tracker('pong'):
            self._profiler.unset()
            self._recorder.finalize()

    def on_function_event(self, frame, event, arg):
        filename, lineno, function, _, _ = \
            inspect.getframeinfo(frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        record = FunctionRecord(self._index, event, function, lineno, filename)
        self._recorder.record(record)
        self._index += 1
