import abc
import functools
import sys


class PikosError(Exception): pass


CO_GENERATOR = 0x0020
def is_generator(f):
    """ Return True if a function is a generator.
    """
    isgen = (f.func_code.co_flags & CO_GENERATOR) != 0
    return isgen


class AbstractMonitor(object):
    """ The base abstract monitor class.

    This is an abstract class for all monitors and  profilers.

    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, item=None, recorder=None):
        """ Class initialization.

        Parameters
        ----------
        item : object
            The item to monitor. The default implementation expects a
            callable object without any arguments.

        recorder :
            An instance of `pikos.recorders.AbstractRecorder`
        """
        self._item = item
        self._recorder = recorder

        self._enable_count = 0

    def run(self, *args, **kwargs):
        """ Start the monitoring.
        """
        self.enable_by_count()
        try:
            return self.run_item(*args, **kwargs)
        finally:
            self.disable_by_count()

    def wrap_generator(self, func):
        """ Wrap a generator to profile it.
        """
        def f(*args, **kwds):
            g = func(*args, **kwds)
            # The first iterate will not be a .send()
            self.enable_by_count()
            try:
                item = g.next()
            finally:
                self.disable_by_count()
            input = (yield item)
            # But any following one might be.
            while True:
                self.enable_by_count()
                try:
                    item = g.send(input)
                finally:
                    self.disable_by_count()
                input = (yield item)
        return f

    def wrap_function(self, func)
        @functools.wraps(item)
        def _profile(*args, **kwargs):
            self.enable_by_count()
            try:
                return func(*args, **kwargs)
            finally:
                self.disable_by_count()
        return _profile

    def __call__(self, func):
        if is_generator(func):
            fn = self.wrap_generator(func)
        else:
            fn = self.wrap_function(func)
        return fn

    def enable_by_count(self):
        if self._enable_count == 0:
            self.setup()
            self.enable()
        self._enable_count += 1

    def disable_by_count(self):
        if self._enable_count > 0:
            self._enable_count -= 1
            if self._enable_count == 0:
                self.disable()

    def enable(self):
        pass

    def disable(self):
        pass

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
