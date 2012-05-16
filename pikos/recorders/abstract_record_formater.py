import abc

class AbstractRecordFormater(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def header(self, record):
        """ Return a formated header for the record. """

    @abc.abstractmethod
    def line(self, record):
        """ Return a formated line for the record. """
