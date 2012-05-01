import sys
try:
    import Threading
except:
    class TraceFunctions(object):

        def set(self, function):
            self._old_function = sys.gettrace()
            sys.settrace(function)

        def unset(self, function):
            sys.settrace(self._old_function)
else:
    class TraceFunctions(object):

        def set(self, function):
            self._old_function = sys.gettrace()
            threading.settrace(function)
            sys.settrace(function)

        def unset(self, function):
            sys.settrace(self._old_function)
            threading.settrace(self._old_function)
