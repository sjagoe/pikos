import unittest

from pikos.monitors.line_monitor import LineMonitor
from pikos.recorders.list_recorder import ListRecorder
from pikos.tests.compat import TestCase


class TestLineMonitor(TestCase):

    def test_issue2(self):
        """ Test for issue #2.

        The issues is reported in `https://github.com/sjagoe/pikos/issues/2`_

        """
        recorder = ListRecorder()
        logger = LineMonitor(recorder)

        FOO = """
def foo():
    a = []
    for i in range(20):
        a.append(i+sum(a))

foo()
"""

        @logger.attach
        def boo():
            code = compile(FOO, 'foo', 'exec')
            exec code in globals(), {}

        try:
            boo()
        except TypeError:
            msg = ("Issue #2 -- line monitor fails when exec is used"
                   " on code compiled from a string -- exists.")
            self.fail(msg)


if __name__ == '__main__':
    unittest.main()
