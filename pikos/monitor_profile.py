# TODO monitor all the children of the application under profiling.
from __future__ import absolute_import

import sys
import time
import datetime
import csv
from psutil import Popen, NoSuchProcess

from pikos.base_profilers import FunctionProfiler

#: CSV file header fields
_fields = ['time', 'name', 'pid', 'mem', 'cpu', 'threads', 'rss', 'vms', 'user',
           'system', 'read_count', 'write_count', 'read_bytes', 'write_bytes']

class MonitorProfile(object):
    """ Profile an application by sampling the cpu, memory and io status.

    The monitor profiler runs the application on a subprocess and monitors
    the cpu, memory and io status at given intervals. The profiler monitors
    also the children (first generation) of the application.

    """
    def __init__(self, command_line, output=None, interval=0.5,
                 verbose=False):
        """ Class Initialisation.

        Arguments
        ---------
        command_line : str
            The command line to start the application that is going to be
            monitored.

        options : dict
            Dictionary of options.

        output : str
            The filename and path where to output the profiling results.

        interval : float
            Time interval in second between process sampling.

        """
        date = datetime.datetime.now()
        name = date.strftime('%Y-%m-%d_%H-%M')  # Year, Month, Day, Hours, Minutes
        self.command_line = command_line
        self.interval = float(interval)
        self.verbose = verbose
        self.output = name if (output is None) else output
        self.info = []
        self.timer = time.clock

    def run(self):
        """ Run the profiler.

        """
        if self.verbose:
            print "MONITOR PROCESS"
        self.sub_process = Popen(self.command_line, shell=False)
        while self.sub_process.is_running():
            self._record_info()
            time.sleep(self.interval)
        self._save_results()

    def _record_info(self):
        """ Record the info for sub_process and its chlidren.
        """
        process = self.sub_process
        try:
            self._record_recursivly(process)
        except NoSuchProcess:
            pass

    def _record_recursivly(self, process):
        """ Recursivly get info for all the child processes
        """
        self._record_process_info(self.timer(), process)
        for child in process.get_children():
            self._record_recursivly(child)

    def _record_process_info(self, time_stamp, process):
        """ Record the process info.
        """
        data = (time_stamp, process.name, process.pid,
                process.get_memory_percent(), process.get_cpu_percent(),
                process.get_num_threads())
        data += process.get_memory_info()
        data += process.get_cpu_times()
        data += process.get_io_counters()
        self.info.append(data)

    def _save_results(self):
        with open(self.output, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(_fields)
            writer.writerows(self.info)
