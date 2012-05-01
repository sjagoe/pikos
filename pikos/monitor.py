import sys
import functools

class Monitor(object):
    """ The base monitor decorator class.

    """
    def __init__(self, monitor_context):
        """ Class initialization.

        """
        self._function = None
        self._monitor_context = monitor_context

    def __call__(self, function):
        self._function = function
        @functools.wraps(function)
        def wrapper(*args, **kwds):
             return self.run(*args, **kwds)
        return wrapper

    def run(self, *args, **kwds):
        """ Start the monitoring.
        """
        with self._monitor_context:
            return self._execute(*args, **kwds)

    def _execute(self, *args, **kwds):
        """ Method prepares and executes the item under examination.

        Anything that the examined item returns should be forwarded
        and returned by this function to the caller (i.e. the :meth:`run`).

        """
        return self._function(*args, **kwds)
