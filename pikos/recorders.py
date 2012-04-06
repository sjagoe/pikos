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
    def record(self, fields, values):
        ''' Record a measurement.

        Parameters
        ----------
        fields : tuple
            Tuple of field names

        values : dict
            A dictionary mapping field name to field value
        '''


class CSVRecorder(object):

    def __init__(self, filename=None):
        if filename is None:
            self._filename = _make_filename()
        else:
            self._filename = filename
        self._output_fh = None
        self._writer = None

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
