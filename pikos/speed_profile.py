from __future__ import absolute_import

import os.path
import cProfile

class SpeedProfile(object):
    """ Speed profiler (deterministic).

    This profiler wraps the standard cProfile library.

    """
    def __init__(self, function, output=None, repeat=1, verbose=False):
        """ Class Initialisation.

        Arguments
        ---------
        function : callable
            A callable object to use

        output : str
            The filename and path where to output the profiling results.

        repeat : int
            Times to repeat the run while profiling.

        """
        self.function = function
        self.repeat = int(repeat)
        self.output = output
        self.verbose = verbose

    def run(self):
        """ Run the profiler.
        """
        if self.verbose:
            print "TIME PROFILE"
        cProfile.runctx('self._runner()', {}, {'self': self}, self.output)

    def _runner(self):
        """ Calulate the case for :attr:`repeat` number of times.
        """
        for _ in range(self.repeat):
            self.function()
