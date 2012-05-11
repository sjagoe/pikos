import csv

from pikos.recorders.abstract_recorder import AbstractRecorder

class CSVRecorder(AbstractRecorder):
    """ The CSV Recorder is a simple text based recorder that records the
    tuple of values using a scv writer.

    Private
    -------
    _filter : callable
        Used to check if the set `record` should be `recored`. The function
        accepts a tuple of the `record` values and return True is the input
        sould be recored.

    _writer : csv.writer
        The `writer` object is owned by the CSVRecorder and exports the record
        values according to the configured dialect.

    _ready : bool
        Singify that the Recorder is ready to accept data. Please use the
        Recorder.ready property

    """

    def __init__(self, stream, filter_=None, **csv_kwargs):
        """ Class initialization.

        Parameters
        ----------
        stream : file
            A *file*-like object to use for output.

        filter_ : callable
            A callable function that accepts a data tuple and returns True
            if the input sould be recorded.

        **csv_kwargs :
            Key word arguments

        """
        self._filter = (lambda x: True) if filter_ is None else filter_
        self._writer = csv.writer(stream, **csv_kwargs)
        self._ready = False

    def prepare(self, fields):
        """ Write the header in the csv file the first time it is called. """
        if not self._ready:
            self._writer.writerow(fields)
            self._ready = True

    def finalize(self):
        """ A do nothing method. """
        pass

    @property
    def ready(self):
        """ Is the recorder ready to accept data? """
        return self._ready

    def record(self, values):
        """ Rerord entry onlty when the filter function returns True. """
        if self._ready and self._filter(values):
            self._writer.writerow(values)
