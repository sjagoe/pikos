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
        foo = self._make_array()
        foo = self._add_to_array(foo, 200.)
        self.leaks.append(foo)

    def _add_to_array(self, array, value):
        return array + value

    def _dont_leak(self):
        foo = self._make_array()
        foo = self._add_to_array(foo, 1.)

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
    for i in xrange(200):
        leaker.run_leaky()
        print proc.get_memory_info()
        leaker.leaks = []
        print proc.get_memory_info()
