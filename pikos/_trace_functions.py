import sys
try:
    import threading
    has_threading = True
except ImportError:
    has_threading = False


class TraceFunctions(object):

    def set(self, function):
        self._old_function = sys.gettrace()
        if has_threading:
            threading.settrace(function)
        sys.settrace(function)

    def unset(self):
        sys.settrace(self._old_function)
        if has_threading:
            threading.settrace(self._old_function)
