from __future__ import absolute_import
import sys
import cProfile

from pikos._internal.keep_track import KeepTrack

__all__ = [
    'PythonCProfiler',
]

class PythonCProfiler(cProfile.Profile):
    """ The normal python cProfiler adapted to work with the pikos Monitor class.


    """
    def __init__(self, *args, **kwrds):
        super(PythonCProfiler, self).__init__(*args, **kwrds)
        self._call_tracker = KeepTrack()

    def __enter__(self):
        if self._call_tracker('ping'):
            self.enable()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._call_tracker('pong'):
            self.disable()

