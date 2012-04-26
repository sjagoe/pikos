from __future__ import absolute_import
import inspect
import os
import sys
import psutil

from functools import wraps
from pikos.abstract_monitors import AbstractMonitor

__all__ = ['FunctionLogger']

class FunctionLogger(AbstractMonitor):

    _fields = ['Type', 'Filename', 'LineNo', 'Function']

    def __init__(self, recorder):
        ''' Initialize the logger class.

        Parameters
        ----------
        function : callable
            The callable to profile

        output : str
            The file in which to store profiling results.

        '''
        super(FunctionLogger, self).__init__(None)
        self._recorder = recorder
        self._process = None
        self._old_profile_function = None

    def __call__(self, function):
        self._item = function
        @wraps(function)
        def wrapper(*args, **kwds):
             return self.run(*args, **kwds)
        return wrapper

    def setup(self):
        self._recorder.prepare(self._fields)
        self._process = psutil.Process(os.getpid())
        self._old_profile_function = sys.getprofile()
        sys.setprofile(self.on_function_event)

    def teardown(self):
        sys.setprofile(self._old_profile_function)
        self._process = None
        self._recorder.finalize()

    def on_function_event(self, frame, event, arg):
        filename, lineno, function, _, _ = \
            inspect.getframeinfo(frame, context=0)
        if event.startswith('c_'):
            function = arg.__name__
        data = (event, filename, lineno, function)
        self._recorder.record(data)


