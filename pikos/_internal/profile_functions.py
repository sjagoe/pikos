import sys
try:
    import threading
    has_threading = True
except ImportError:
    has_threading = False


class ProfileFunctions(object):
    """ A Class to handle setting and unseting the setprofile function.

    """

    def set(self, function):
        """ Set a new function in sys.setprofile.

        """
        if has_threading:
            threading.setprofile(function)
        sys.setprofile(function)

    def unset(self):
        """ Unset the current function in the sys.setprofile.
        """
        sys.setprofile(None)
        if has_threading:
            threading.setprofile(None)
