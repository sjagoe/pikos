_MODES = {'setup': 1, 'teardown': -1}
_CHECKS = {'setup': 1, 'teardown': 0}

class KeepTrack(object):
    """ A simple object to keep track of setup and teardown calls\

    The object is used to decide if a initialization or destroy operation needs
    to be performed when a context manager is called recursivly.

    usage:
        - Calling the instance with ``mode='setup'`` will increase the
          internal counter and return true only the first time it is called.
        - Calling the instance with ``mode='teardown'`` will decrease the
          internal counter and return False until the counter is zero which
          will pair with the first time the instance was called.

    """
    def __init__(self):
        self._counter = 0

    def __call__(self, mode='setup'):
        """

        Parameters
        ----------
        mode : string
            mode is a String with value 'setup' or 'teardown' to indicate the
            operation that is perfomed in the internal counter.

        Returns
        -------
        A boolean value inidicating that an actual *setup* or *teardown* needs
        to be perfomed.

        """
        self._counter += _MODES[mode]
        if self._counter < 0:
            self._counter = 0
            return False
        else:
            return self._counter==_CHECKS[mode]
