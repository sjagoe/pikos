import sys
try:
    import threading
    has_threading = True
except ImportError:
    has_threading = False


class ProfileFunctions(object):

    def set(self, function):
        self._old_function = sys.getprofile()
        if has_threading:
            threading.setprofile(function)
        sys.setprofile(function)

    def unset(self):
        sys.setprofile(self._old_function)
        if has_threading:
            threading.setprofile(self._old_function)
