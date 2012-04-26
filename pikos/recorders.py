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

    def __init__(self, filename=None):
        self._filename = _make_filename() if (filename is None) else filename
        self._csvfile = open(self._filename, 'wb', buffering=0)
        self._writer = csv.writer(self._csvfile)
        self._started = False

    def prepare(self, fields):
        if not self._started:
            self._writer.writerow(fields)
            self._started = True

    def finalize(self):
        pass

    def record(self, values):
        self._writer.writerow(values)

    def prepare(self, fields):
        self._output_fh = open(self._filename, 'wb', buffering=0)
        self._writer = csv.writer(self._output_fh)
        self._writer.writerow(fields)

    def finalize(self):
        self._output_fh.close()
        self._output_fh = None
        self._writer = None

    def record(self, fields, values):
        try:
            line = [values[field] for field in fields]
        except KeyError:
            raise RecorderError(
                'Invalid value dictionary. Expected keys {0!r}, got {1!r}'.\
                    format(fields, values.keys()))
        self._writer.writerow(line)
