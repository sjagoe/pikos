from __future__ import absolute_import
import abc
import sys

class ProfilerError(Exception):
    """ Base profiler error.
    """
    pass

# TODO make this class a base class of the profiler higherarchy.
class AbstractProfiler(object):
    """ The base profiler class.

    This is an abstract class for all the profiles.


    """
    def __init__(self, function, verbose=False):
        """Class Initialisation.

        Arguments
        ---------
        function : callable object
            The callable objects under examination

        """
        self.function = function
        self.verbose = verbose

    def run(self):
        """Run the code under examination.
        """
        self.start()
        try:
            result = self.function()
        except Exception as error:
            msg = "This error occured while running the provided code: {0}".\
                    format(error)
            ProfilerError(msg)
        finally:
            self.stop()
        return result

    @abc.abtsractmethod
    def start(self):
        """Setup profiling.
        """
        pass

    @abc.abtsractmethod
    def stop(self):
        """Stop profiling.
        """
        pass

class FunctionProfiler(AbstractProfiler):
    """Abstract profiler on function events through the setprofile
    interface.
    """

    def start(self):
        """Setup profiling.
        """
        sys.setprofile(self.on_function_event)

    def stop(self):
        sys.setprofile(None)

    @abc.abstractmethod
    def function_event(self, frame, event, arg):
        """Function event despatcher.
        """
        pass

class LineProfiler(AbstractProfiler):
    """Abstract profiler invoced on every line executed through the settrace
    interface.
    """

    def start(self):
        """Setup profiling.
        """
        sys.settrace(self.on_line)

    def on_stop(self):
        sys.settrace(None)

    @abc.abstractmethod
    def on_line_event(self, frame, event, arg):
        """Line event despatcher.
        """
        pass






