import abc
import csv
from datetime import datetime

from pikos.abstract_monitors import PikosError


class RecorderError(PikosError): pass


def _make_filename():
    time = datetime.now()
    return '{0}.profile'.format(time.strftime('%Y-%m-%d_%H-%M-S'))


class AbstractRecorder(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def prepare(self):
        ''' Perform any setup required before the recorder is used
        '''

    @abc.abstractmethod
    def finalize(self):
        ''' Perform any tasks to finalize and clean up when the
        recording is completed
        '''

    @abc.abstractmethod
    def record(self, *args, **kwargs):
        ''' Record a measurement. '''

class CSVRecorder(AbstractRecorder):

    def __init__(self, filename=None, record_filter=None):
        self._filename = _make_filename() if (filename is None) else filename
        self._csvfile = open(self._filename, 'wb', buffering=0)
        self._writer = csv.writer(self._csvfile)
        self._started = False
        if record_filter is None:
            record_filter = lambda x: True
        self._record_filter = record_filter

    def prepare(self, fields):
        if not self._started:
            self._writer.writerow(fields)
            self._started = True

    def finalize(self):
        pass

    def record(self, values):
        if self._record_filter(values):
            self._writer.writerow(values)

class ConsoleRecorder(AbstractRecorder):

    def __init__(self, record_filter=None):
        if record_filter is None:
            record_filter = lambda x: True
        self._record_filter = recorde_filter

    def prepare(self, fields):
        print "RECORDING STARTS"

    def finalize(self):
        print "RECORDING FINISHED"

    def record(self, values):
        print values

