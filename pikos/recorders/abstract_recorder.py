import abc

class RecorderError(Exception):
        pass

class AbstractRecorder(object):
    """ Abstract recorder class. """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def prepare(self, fields):
        """ Perform any setup required before the recorder is used. """

    @abc.abstractmethod
    def finalize(self):
        """ Perform any tasks to finalize and clean up when the recording
        is completed.

        """

    @abc.abstractmethod
    def record(self, values):
        """ Record a measurement. """
