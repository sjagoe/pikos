import os.path
import datetime
import sys
import os
import inspect
import gc
import csv
import psutil

_fields = ['Type', 'Filename', 'LineNo', 'Name', 'RSS', 'VMS']

_cond_fields = ['Index', 'Type', 'Depth', 'Filename',
                'LineNo', 'Name', 'RSS', 'VMS']

# TODO: I am not sure if exception events should be considered
# TODO: Subtract the size of the MemoryProfile object from the memory usage

class MemoryProfile(object):
    """ Profile the memory usage of a function.

    The profiler hooks itself in the python profile event hook and records
    the current process memory info at function call and return. The
    results for each event are saved into an csv file as defined by the
    ``output`` attribute. The csv header is as follows:

    ========== ===========================================================
    Field      Description
    ========== ===========================================================
    Index      The current event index (only used when condenced is True).
    Type       The type of record (see profile events).
    Depth      The depth in the call stack of the function.
    Filename   The filename where the function leaves.
    Lineno     The current line number.
    Name       The name of the function.
    RSS        The RSS memory on the event.
    VMS        The VMS memory on the event.
    ========== ===========================================================

    .. note::
        - The memory usage is given for the current process.

    """
    def __init__(self, function, output=None, no_gc=True, condensed=False,
                 acceptable=None, at_function=None, verbose=False):
        """ Class Initialisation.

        Arguments
        ---------
        function : callable
            The callable object to profile.

        output :
            The folder where to output the profiling results.

        no_gc :
            Enable/Disable garbage collection during profiling.


        condensed :
            Records will be kept only when the memory usage has changed.

        """
        date = datetime.datetime.now()
        name = date.strftime('%Y-%m-%d_%H-%M')  # Year, Month, Day, Hours, Minutes
        self.function = function
        self.output = name if output is None else output
        self.no_gc = no_gc
        self.verbose = verbose
        self.depth = 0
        self.index = 0
        if acceptable is not None:
            try:
                names = set(acceptable.split(','))
            except AttributeError:
                self.acceptable = acceptable
            else:
                names = [name.strip() for name in names]
                self.acceptable = names
        else:
            self.acceptable = acceptable
        self.at_function = at_function
        if at_function is None:
            self.condensed = condensed
        else:
            self.condensed = False
            self.acceptable = None

        self._setup_methods()

    def run(self, *args, **kwds):
        """ Run the profiler.
        """
        if self.verbose:
            print "MEMORY PROFILING"

        self._open_output_file()
        if self.no_gc:
            gc.disable()

        self.current = self._get_memory_info()
        sys.setprofile(self._record)
        try:
            self.function(*args, **kwds)
        finally:
            sys.setprofile(None)
            gc.enable()
            self._close_output_file()

    def _setup_methods(self):
        """ Setup the appropriate optimized method for profiling

        The assigns the optimised methods to the default profiling methods
        of the class. The methods are optimized given the platform and
        initialization options.

        """
        self._setup_get_memory()
        if (self.acceptable is not None) and self.condensed:
            self._record = self._record_filter_diff
        elif self.condensed:
            self._record = self._record_diff
        elif self.acceptable is not None:
            self._record = self._record_filter
        else:
            if self.at_function is None:
                self._record = self._record_full
            else:
                self._record = self._record_full_at_function

    def _setup_get_memory(self):
        """ Set the memory method based on the current platform

        """
        self.process = psutil.Process(os.getpid())

    def _get_memory_info(self):
        return self.process.get_memory_info()

    def _record_full(self, frame, event, arg):
        """ Record full function and memory usage.
        """
        usage = self._get_memory_info()
        filename, lineno, function, _, _ = inspect.getframeinfo(frame, context=0)
        if 'c_' in event:
            function = arg.__name__
        record = (event, filename, lineno, function, usage.rss, usage.vms)
        self.writerow(record)

    def _record_full_at_function(self, frame, event, arg):
        """ Record full function and memory usage during the predefined
        function call.

        """

        usage = self._get_memory_info()
        if 'c_' in event:
            function = arg.__name__
        else:
            function = frame.f_code.co_name

        if self.at_function == function:
           if 'call' in event:
                self.index += 1
           else:
                self.index -= 1

        if self.index > 0:
            filename, lineno, _, _, _ = inspect.getframeinfo(frame, context=0)
            record = (event, filename, lineno, function, usage.rss, usage.vms)
            self.writerow(record)

    def _record_diff(self, frame, event, arg):
        """ Record execution info only when memory usage changed.
        """
        usage = self._get_memory_info()
        self.index += 1
        self.depth += 1 if 'call' in event else -1
        if usage != self.current:
            filename, lineno, function, _, _ = \
                inspect.getframeinfo(frame, context=0)
            if 'c_' in event:
                function = arg.__name__
            record = (self.index, event, self.depth,
                      filename, lineno, function, usage.rss, usage.vms)
            self.writerow(record)
            self.current = usage

    def _record_filter(self, frame, event, arg):
        """ Record execution info only when the function is one of the
            acceptable names.
        """
        usage = self._get_memory_info()
        self.index += 1
        self._update_depth(event)
        if 'c_' in event:
            function = arg.__name__
        else:
            function = frame.f_code.co_name
        if function in self.acceptable:
            filename, lineno, _, _, _ = \
                inspect.getframeinfo(frame, context=0)
            record = (self.index, event, self.depth,
                      filename, lineno, function, usage.rss, usage.vms)
            self.writerow(record)

    def _record_filter_diff(self, frame, event, arg):
        """ Record execution info only when the function is one of the
            acceptable names or the memory usage changed.
        """
        usage = self._get_memory_info()
        self.index += 1
        self._update_depth(event)
        if 'c_' in event:
            function = arg.__name__
        else:
            function = frame.f_code.co_name
        if (function in self.acceptable) or self.current != usage:
            filename, lineno, _, _, _ = \
                inspect.getframeinfo(frame, context=0)
            record = (self.index, event, self.depth,
                      filename, lineno, function, usage.rss, usage.vms)
            self.writerow(record)
            self.current = usage

    def _update_depth(self, event):
        if 'call' in event:
            self.depth += 1
        else:
            self.depth -= 1

    def _open_output_file(self):
        self.handle = open(self.output, 'wb', buffering=0)
        self.writer = csv.writer(self.handle)
        self.writerow= self.writer.writerow
        if self.condensed:
            self.writerow(_cond_fields)
        else:
            self.writerow(_fields)

    def _close_output_file(self):
        self.handle.close()
