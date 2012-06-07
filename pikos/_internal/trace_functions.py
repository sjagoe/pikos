import sys
try:
    import threading
    has_threading = True
except ImportError:
    has_threading = False


class TraceFunctions(object):
    """ A Class to handle setting and unseting the settrace function.

    """

    def set(self, function):
        """ Set a new function in sys.setprofile.

        """
        if has_threading:
            threading.settrace(function)
        sys.settrace(function)

    def unset(self):
        """ Unset the current function in the sys.setprofile.
        """
        sys.settrace(None)
        if has_threading:
            threading.settrace(None)

