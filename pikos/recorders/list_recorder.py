import csv

from pikos.recorders.abstract_recorder import AbstractRecorder

class ListRecorder(AbstractRecorder):
    """ The  ListRecorder is simple recorder that records the
    tuple of values in memory as a list.

    Public
    ------
    records : list
        List of records. The Recorder assumes that the record method is
        provided with a tuple and accumulates all the records in a list.

    Private
    -------
    _filter : callable
        Used to check if the set `record` should be `recored`. The function
        accepts a tuple of the `record` values and return True is the input
        sould be recored.

    """

    def __init__(self, filter_=None):
        """ Class initialization.

        Parameters
        ----------

        filter_ : callable
            A callable function that accepts a data tuple and returns True
            if the input sould be recorded.

        """
        self._filter = (lambda x: True) if filter_ is None else filter_
        self.records = []

    def prepare(self, fields):
        """ A do nothing method. """
        pass

    def finalize(self):
        """ A do nothing method. """
        pass

    @property
    def ready(self):
        """ Is the recorder ready to accept data? """
        return True

    def record(self, values):
        """ Rerord entry onlty when the filter function returns True. """
        if self.ready and self._filter(values):
            self.records.append(values)
