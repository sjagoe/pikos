from __future__ import absolute_import
import sys
import cProfile
import profile


__all__ = [
    'PythonCProfiler',
]

class PythonCProfiler(cProfile.Profile):
    """ The normal python cProfiler adapted to work with the pikos Monitor class.
    """
    def __init__(self, *args, **kwrds):
        super(PythonCProfiler, self).__init__(*args, **kwrds)
        self._run_count = 0

    def __enter__(self):
        self._run_count += 1
        if self._run_count == 1:
            self.enable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._run_count -= 1
        if self._run_count == 0:
            self.disable()

