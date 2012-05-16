import os

from pikos.recorders.abstract_recorder import AbstractRecorder, RecorderError

class TextStreamRecorder(AbstractRecorder):
    """ The TextStreamRecorder is simple recorder that formats and writes the
    records directly to a stream.

    The output of the Recorder is controled by the formating

    Private
    -------

    _stream : TextIOBase
        A text stream what supports the TextIOBase interface. The Recorder will
        write the values as a single line.

    _filter : callable
        Used to check if the set `record` should be `recorded`. The function
        accepts a tuple of the `record` values and return True is the input
        sould be recored.

    _tamplate : str
        A string (using the `Format Specification Mini-Language`) to format the
        set of values in a line. It is constructed when the `prepare` method is
        called.

    _ready : bool
        Singify that the Recorder is ready to accept data.

    """

    def __init__(self, text_stream, filter_=None, formater=None):
        """ Class initialization.

        Parameters
        ----------
        text_stream : TextIOBase
            A text stream what supports the TextIOBase interface.

        filter_ : callable
            A callable function that accepts a data tuple and returns True
            if the input sould be recorded.

        formater : class
            A concrit class that implements the the RecordFormater interface.
            Default is no formating.

        """
        self._filter = (lambda x: True) if filter_ is None else filter_
        self._stream = text_stream
        self._formater = formater
        self._ready = False

    def prepare(self, record):
        """ Setup the format template. """
        if not self._ready:
            self._writeheader(record)
            self._ready = True

    def finalize(self):
        """ A do nothing method. """
        if not self._ready:
            msg = 'Method called while recorder has not been prepared yet'
            raise RecorderError(msg)

    def record(self, record):
        """ Record entry only when the filter function returns True. """
        if self._ready:
            if self._filter(record):
                line = self._format(record)
                self._stream.write(line)
        else:
            msg = 'Method called while recorder is not ready to record'
            raise RecorderError(msg)

    def _writeheader(self, record):
        """ Write the header to the stream. """
        if self._formater is None:
            header = self._format(record._fields)
        else:
            header = self._formater.header(record)
        separator = '-' * (len(header) - len(os.linesep)) + os.linesep
        self._stream.write(header)
        self._stream.write(separator)

    def _format(self, record):
        """ Format the record values"""
        if self._formater is None:
            line = ' '.join(str(value) for value in record) + os.linesep
        else:
            line = self._formater.line(record)
        return line
