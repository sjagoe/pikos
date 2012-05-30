import os

import numpy as np
import psutil

from pikos.api import monitor, baserecorder
from pikos.monitors.function_memory_monitor import FunctionMemoryMonitor
from pikos.recorders.zeromq_recorder import ZeroMQRecorder


class Leaker(object):

    def __init__(self, number, shape):
        self.number = number
        self.shape = shape
        self.leaks = []

    def _make_array(self):
        return np.empty(self.shape)

    def _leak(self):
        self.leaks.append(self._make_array())

    def _dont_leak(self):
        self._make_array()

    @monitor(FunctionMemoryMonitor(ZeroMQRecorder()))
    # @monitor(log_functions())
    def run_leaky(self):
        for i in xrange(self.number):
            self._leak()
            self._dont_leak()


if __name__ == '__main__':
    proc = psutil.Process(os.getpid())
    print proc.get_memory_info()
    leaker = Leaker(1000, (100, 100))
    leaker.run_leaky()
    print proc.get_memory_info()
