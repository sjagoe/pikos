""" Memory profiler """
import inspect
import csv

from pikos.base_profilers import FunctionProfiler

_fields = ['Type', 'Filename', 'LineNo', 'Name']

# TODO: I am not sure if exception events should be considered
# TODO: Subtract the size of the MemoryProfile object from the memory usage

class FunctionLogger(FunctionProfiler):
    """ Monitor and log the function calls during a run

    The hooks itself in the python profile event hook and records
    the info at function call and return. The results for each event are
    saved into an csv file as defined by the ``output`` attribute. The csv
    header is as follows:

    ========== ==========================================================
    Field      Description
    ========== ==========================================================
    Type       The type of record (see profile events).
    Filename   The filename where the function lives.
    Lineno     The current line number.
    Name       The name of the function.
    ========== ==========================================================

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

    def stop(self):
        """Overide the default stop method to save the function information.
        """
        super(FunctionLogger, self).stop()
        self._save_log()

    def _save_log(self):
        """Save the function event log to file using an csv writer.
        """
        with open(self.output, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(_fields)
            writer.writerows(self.info)
