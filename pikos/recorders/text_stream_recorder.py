import os

from pikos.recorders.abstract_recorder import AbstractRecorder, RecorderError

class TextStreamRecorder(AbstractRecorder):
    """ The TextStreamRecorder is simple recorder that formats and writes the
    records directly to a stream.

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

    def __init__(self, text_stream, filter_=None):
        """ Class initialization.

        Parameters
        ----------
        text_stream : TextIOBase
            A text stream what supports the TextIOBase interface.

        filter_ : callable
            A callable function that accepts a data tuple and returns True
            if the input sould be recorded.

        """
        self._filter = (lambda x: True) if filter_ is None else filter_
        self._stream = text_stream
        self._template = None
        self._ready = False

    def prepare(self, fields):
        """ Setup the format template. """
        if not self._ready:
            self._setup_template(fields)
            self._writeheader(fields)
            self._ready = True

    def finalize(self):
        """ A do nothing method. """
        if not self._ready:
            msg = 'Method called while recorder has not been prepared yet'
            raise RecorderError(msg)

    def record(self, values):
        """ Record entry only when the filter function returns True. """
        if self._ready:
            if self._filter(values):
                line = self._format(values)
                self._stream.write(line)
        else:
            msg = 'Method called while recorder is not ready to record'
            raise RecorderError(msg)

    def _format(self, values, max_length=30):
        """ Format the record """
        str_values = [str(value)[-max_length:len(str(value))]
                     for value in values]
        return self._template.format(*str_values)

    def _writeheader(self, fields):
        """ Write the header to the stream. """
        header = self._format(fields)
        separator = '{:-<{length}}{}'.format('', os.linesep,
                                            length=len(header)-len(os.linesep))
        self._stream.write(header)
        self._stream.write(separator)

    def _setup_template(self, fields):
        """ Setup the template to write the fields. """
        template = '{:<30} ' * len(fields)
        template = template.strip() + os.linesep
        self._template = template
