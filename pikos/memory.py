from __future__ import absolute_import
import sys
import os
import inspect
import gc
import csv
import argparse
import psutil

from pikos.abstract_monitors import AbstractFunctionMonitor, AbstractTimeMonitor


# FIXME now!!!
if 'win' in sys.platform:
    import win32api
    from win32process import GetProcessMemoryInfo
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

_fields = ['Type', 'Filename', 'LineNo', 'Name', 'RSS']

_cond_fields = ['Index', 'Type', 'Depth', 'Filename', 'LineNo', 'Name', 'RSS']


class MemoryMonitor(AbstractTimeMonitor):

    def on_function_event(self, frame, event, arg):
        """ Record function info.
        """
        if 'c_' in event:
            function_name = arg.__name__
        else:
            function_name = frame.f_code.co_name
        filename, lineno, _, _, _ = inspect.getframeinfo(frame, context=0)
        record = (event, filename, lineno, function_name)
        self.info.append(record)

    def teardown(self):
        """Overide the default stop method to save the function information.
        """
        super(FunctionLogger, self).stop()
        self._save_log()

    def _save_record(self):
        """Save the function event log to file using an csv writer.
        """
        with open(self.output, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(_fields)
            writer.writerows(self.info)


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
    ========== ===========================================================

    .. note::
        - The memory usage is given for the current process.

    """
    def __init__(self, function, output=None):
        """ Function Logger class Initialisation.

        Arguments
        ---------
        function : callable
            The callable object to whos functions will be logged.

        output :
            The filename to output the profiling results. Default value is
            ``function_trace.log``.

        """
        super(FunctionLogger, self).__init__(function)
        self.output = 'function_trace.log' if (output is None) else output
        self.info = []
        self.current = 0

    def setup(self):
        """ Setup the class to start profiling

        """
        super(
        self._open_output_file()
        if self.no_gc:
            gc.disable()
        self.current = self._get_memory_info()

    def teardown(self):
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

        In windows platforms the win32api library is used to abvoid a bug
        in psutil 0.4.0.

        """
        if 'win' in sys.platform:
            open_constants = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
            self.process = win32api.OpenProcess(open_constants, False,
                                                os.getpid())
            self._get_memory_info = self._get_memory_info_win
        else:
            self.process = psutil.Process(os.getpid())
            self._get_memory_info = self._get_memory_info_default

    def _get_memory_info_default(self):
        return self.process.get_memory_info().rss

    def _get_memory_info_win(self):
        return GetProcessMemoryInfo(self.process)['WorkingSetSize']

    def _record_full(self, frame, event, arg):
        """ Record full function and memory usage.
        """
        usage = self._get_memory_info()
        filename, lineno, function, _, _ = inspect.getframeinfo(frame, context=0)
        if 'c_' in event:
            function = arg.__name__
        record = (event, filename, lineno, function, usage)
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
            record = (event, filename, lineno, function, usage)
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
                      filename, lineno, function, usage)
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
                      filename, lineno, function, usage)
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
                      filename, lineno, function, usage)
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
