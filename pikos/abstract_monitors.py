import abc
import sys

class PikosError(Exception):
    """ Base pikos error.
    """
    pass

class AbstractMonitor(object):
    """ The abstract monitor class.

    This is an abstract class for all the profiles.


    """
    def run(self):
        """Run the code under examination.
        """
        self.setup()
        try:
            result = self.process()
        except Exception as error:
            msg = "This error occured while running the provided code: {0}".\
                    format(error)
            PikosError(msg)
        finally:
            self.teardown()
        return result

    @abc.abtsractmethod
    def setup(self):
        """Setup the monitor.
        """
        pass

    @abc.abtsractmethod
    def teardown(self):
        """Tear down the monitor.
        """
        pass

    @abc.abstractmethod
    def process(self):
        """process to executed during monitoring.
        """
        pass


class AbstractTimeMonitor(AbstractMonitor):
    """Abstract monitor over fixed time itervals.
    """
    def __init__(self, interval=250):
        """Class Initialisation.
        """
        self.interval = interval

    def process(self):
        while self.reset_timer():
            self.on_time_event()
            time.sleep(self.interval)

    @abc.abstractmethod
    def reset_timer(self):
        """ check if we need to reset the timer and continue monitoring.
        """
        return False

    @abc.abstractmethod
    def on_time_event(self):
        """Line event despatcher.
        """
        pass


class AbstractFunctionMonitor(AbstractProfiler):
    """Abstract monitor for function events using the setprofile interface.
    """
    def __init__(self, callable):
        """Class Initialisation.
        """
        self.process = callable

    def setup(self):
        sys.setprofile(self.on_function_event)

    def teardown(self):
        sys.setprofile(None)

    @abc.abstractmethod
    def on_function_event(self, frame, event, arg):
        """Function event despatcher.
        """
        pass


class AbstractLineMonitor(AbstractMonitor):
    """Abstract monitor using the settrace interface.
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
        """Line event despatcher.
        """
        pass
