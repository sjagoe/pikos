import sys
try:
    import Threading
except:
    class ProfileFunctions(object):

        def set(self, function):
            self._old_function = sys.getprofile()
            sys.setprofile(function)

        def unset(self):
            sys.setprofile(self._old_function)
else:
    class ProfileFunctions(object):

        def set(self, function):
            self._old_function = sys.getprofile()
            threading.setprofile(function)
            sys.setprofile(function)

        def unset(self):
            sys.setprofile(self._old_function)
            threading.setprofile(self._old_function)
