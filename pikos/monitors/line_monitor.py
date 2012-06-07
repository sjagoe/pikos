from __future__ import absolute_import
import inspect

from collections import namedtuple
from pikos._internal.trace_functions import TraceFunctions
from pikos._internal.keep_track import KeepTrack
from pikos.recorders.abstract_record_formater import AbstractRecordFormater

__all__ = [
    'LineMonitor',
    'LineRecord',
    'LineRecordFormater'
]

LINE_RECORD = ('index', 'function', 'lineNo', 'line', 'filename')
LINE_RECORD_TEMPLATE = '{:<12} {:<50} {:<7} {} {}{newline}'

LineRecord = namedtuple('LineRecord', LINE_RECORD)

class LineRecordFormater(AbstractRecordFormater):

    def header(self, record):
        return LINE_RECORD_TEMPLATE.format(*record._fields, newline=os.linesep)

    def line(self, record):
        return LINE_RECORD_TEMPLATE.format(*record, newline=os.linesep)


class LineMonitor(object):
    """ Log python line events """

    def __init__(self, recorder):
        """ Initialize the monitoring class.

        Parameters
        ----------
        recorder : pikos.recorders.AbstractRecorder
            An instance of a pikos recorder to handle the values to be logged
        """
        self._recorder = recorder
        self._tracer = TraceFunctions()
        self._index = 0
        self._call_tracker = KeepTrack()

    def __enter__(self):
        if self._call_tracker('ping'):
            self._recorder.prepare(LineRecord)
            self._tracer.set(self.on_line_event)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._call_tracker('pong'):
            self._tracer.unset()
            self._recorder.finalize()

    def on_line_event(self, frame, why, arg):
        if why.startswith('l'):
            filename, lineno, function, line, index = \
                inspect.getframeinfo(frame, context=1)
            record = LineRecord(self._index, function, lineno, line[0].rstrip(),
                                filename)
            self._recorder.record(record)
            self._index += 1
        return self.on_line_event
