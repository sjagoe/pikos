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
            The item to monitor.

        """
        self._item = item

    def run(self):
        """ Start the monitoring.
        """
        self.setup()
        try:
            result = self.monitor_item()
        finally:
            self.teardown()
        return result

    @abc.abtsractmethod
    def setup(self):
        """ Setup the monitor.
        """
        pass

    @abc.abtsractmethod
    def teardown(self):
        """ Tear-down the monitor.
        """
        pass

    @abc.abstractmethod
    def monitor_item(self):
        """ Method executes the item under examination.

        Anything that the examined item returns should be forwarded
        and returned by this function to the caller.

        """
        pass


class AbstractFunctionMonitor(AbstractMonitor):
    """ Abstract monitor on function events using the setprofile interface.
    """
    def __init__(self, callable):
        self.process = callable

    def setup(self):
        sys.setprofile(self.on_function_event)

    def teardown(self):
        sys.setprofile(None)

    @abc.abstractmethod
    def on_function_event(self, frame, event, arg):
        """ Function event dispatcher.
        """
        pass


class AbstractLineMonitor(AbstractMonitor):
    """ Abstract monitor using the settrace interface.
    """
    def __init__(self, callable):
        """ Class Initialisation.
        """
        self.process = callable

    def setup(self):
        sys.settrace(self.on_line_event)

    def teardown(self):
        sys.settrace(None)

    @abc.abstractmethod
    def on_line_event(self, frame, event, arg):
        """ Line event despatcher.
        """
        pass


class AbstractTimeMonitor(AbstractMonitor):
    """ Abstract monitor to examine an external process over fixed
    time itervals.

    A TimeMonitor should setup a timer in the :meth:`setup` method
    that will call the :meth:`on_time_event` to record the necessary
    information.

    """
    def __init__(self, interval):
        self.interval = interval

    @abc.abstractmethod
    def on_time_event(self):
        """Line event despatcher.
        """
        pass
