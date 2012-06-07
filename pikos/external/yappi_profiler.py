from __future__ import absolute_import

from collections import namedtuple

import yappi


__all__ = [
    'YappiProfiler',
]

class YappiProfiler(object):
    """ A pikos compatible profiler class using the yappi library. """

    def __init__(self, recorder=None, builtins=False):
        """ Initialize the profiler class.

        Parameters
        ----------
        builtins : bool
            When set python builtins are also profilered.

        """
        self._builtins = builtins

    def __enter__(self):
        if yappi.is_running():
            yappi.start(self._builtins)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if yappi.is_running:
            yappi.stop()

    def start(self, builtins=None):
        builtins = self.builtins if builtins is None else builtins
        yappi.start(builtins)

    def stop(self):
        yappi.stop()

    def enum_stats(self, fenum):
        return yappi.enum_stats(fenum)

    def enum_thread_stats(self):
        return yappi.enum_thread_stats()

    def get_stats(self, *args, **kwrds):
        return yappi.get_stats(*args, **kwrds)

    def print_stats(self, *args, **kwrds):
        yappi.print_stats(*args, **kwrds)

    def clear_stats(self):
        yappi.clear_stats()

    def is_running(self):
        return yappi.is_running()

    def clock_type(self):
        return yappi.clock_type()