import inspect
import functools

from pikos._internal.util import is_context_manager

class _MonitorAssistant(object):
    """ The monitor class decorator.

    This is the main entry point for all the monitors, inspectors, loggers and
    profilers that are supported by pikos. The MonitoAssistant is tring to be
    as versitile as possible in order to simplify setting up and invoking the
    actual monitoring/profiling class.

    The class can be instanciated by the user or used as a decorator -- throught
    the monitor alias -- for functions, methods and generators.

    Usage
    -----

    # as a decorator
    @monitor(FunctionLogger())
    def my_function():
        ...
        return

    # as an instance
    def my_function():
        ...
        return

    logfunctions = MonitorAssistant(FunctionLogger(), )
    logfunctions(my_function, *args, **kwrgs)
    ...

    """
    def __init__(self, obj):
        """ Class initialization.

        """
        self._function = None
        self._monitor_object = obj

    def __call__(self, function):
        self._function = function
        if is_context_manager(self._monitor_object):
            return self._use_context_manager()
        else:
            return self._use_runcall()

    def _use_context_manager(self):
        if inspect.isgeneratorfunction(self._function):
            self._is_generator = True
            fn = self.wrap_generator_with_context_manager()
        else:
            fn = self.wrap_function_with_context_manager()
        return fn

    def _use_runcall(self):
        if inspect.isgeneratorfunction(self._function):
            fn = self.wrap_generator_with_runcall()
        else:
            fn = self.wrap_function_with_runcall()
        return fn

    def wrap_function_with_runcall(self):
        @functools.wraps(self._function)
        def wrapper(*args, **kwds):
             monitor = self._monitor_object
             return monitor.runcall(self._function, *args, **kwds)
        return wrapper

    def wrap_generator_with_runcall(self):
        """ Wrap a generator to profile it.
        """
        def wrapper(*args, **kwds):
            g = self._function(*args, **kwds)
            monitor = self._monitor_object
            # The first iterate will not be a .send()
            value = (yield monitor.runcall(g.next))
            # But any following one might be.
            while True:
                item = monitor.runcall(g.send, (value,))
                value = (yield item)
        return wrapper

    def wrap_function_with_context_manager(self):
        @functools.wraps(self._function)
        def wrapper(*args, **kwds):
            with self._monitor_object:
                 return self._function(*args, **kwds)
        return wrapper

    def wrap_generator_with_context_manager(self):
        """ Wrap a generator to profile it.
        """
        def wrapper(*args, **kwds):
            g = self._function(*args, **kwds)
            # The first iterate will not be a .send()
            with self._monitor_object:
                value = g.next()
            yield value
            # But any following one might be.
            while True:
                with self._monitor_object:
                    item = g.send(value)
                value = (yield item)
        return wrapper

Monitor = _MonitorAssistant
monitor = _MonitorAssistant