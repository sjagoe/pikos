import abc

class AbstractRecorder(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def prepare(self):
        """ Perform any setup required before the recorder is used. """

    @abc.abstractmethod
    def finalize(self):
        """ Perform any tasks to finalize and clean up when the recording
        is completed.

        """

    @abc.abstractmethod
    def record(self, *args, **kwargs):
        """ Record a measurement. """

    @abc.abstractproperty
    def ready(self):
        """ Indicate that the recorder is ready to receive data. """
