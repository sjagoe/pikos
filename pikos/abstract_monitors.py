import abc
import sys

class AbstractMonitor(object):
    """ The base abstract monitor class.

    This is an abstract class for all monitors and  profilers.

    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, item):
        """ Class initialization.

        Parameters
        ----------
        item : object
            The item to monitor. The default implementation expects a
            callable object without any arguments.

        """
        self._item = item

    def run(self):
        """ Start the monitoring.
        """
        self.setup()
        try:
            return self.run_item()
        finally:
            self.teardown()

    @abc.abstractmethod
    def setup(self):
        """ Setup the monitor.
        """
        pass

    @abc.abstractmethod
    def teardown(self):
        """ Tear-down the monitor.
        """
        pass

    def run_item(self):
        """ Method prepares and executes the item under examination.

        Anything that the examined item returns should be forwarded
        and returned by this function to the caller (i.e. the :meth:`run`).

        """
        return self._item()


class AbstractTimeMonitor(AbstractMonitor):
    """ Abstract monitor to examine an external process over fixed
    time itervals.

    """
    def __init__(self, item, interval):
        super(AbstractMonitor, self).__init__(item)
        self.interval = interval

    @abc.abstractmethod
    def on_time_event(self):
        """Line event despatcher.
        """
        pass
