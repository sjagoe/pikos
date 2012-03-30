# TODO monitor all the children of the application under profiling.
from __future__ import absolute_import

import csv
import sys
import time
import multiprocessing import Process

from psutil import Popen, NoSuchProcess

from pikos.abstract_monitors import AbstractTimeMonitor

#: CSV file header fields
_fields = ['time', 'name', 'pid', 'mem', 'cpu', 'threads', 'rss', 'vms', 'user',
           'system', 'read_count', 'write_count', 'read_bytes', 'write_bytes']

class ProcessMonitor(AbstractTimeMonitor):
    """ Monitors an application by sampling the cpu, memory and io status.

    The monitor runs the code on a separate process and monitors the
    cpu, memory and io status at given intervals. The class
    monitors also all the children (i.e subprocesses).

    """
    def __init__(self, command_line, output, interval=250):
        """ Class Initialisation.

        Arguments
        ---------
        command_line : str
            The command line to execute.

        output : str
            The filename and path where to output the profiling results.

        interval : float
            Time interval in second between process sampling.

        """
        super(ProcessMonitor, self).__init__(interval)
        self.command_line = command_line
        self.interval = float(interval)
        self.info = []
        self.timer = time.clock

    def setup(self):
        self.sub_process = Popen(self.command_line, shell=False)

    def teardown(self):
        self._save_results()

    def reset_timer(self)

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
