import unittest

from pikos.monitor import Monitor as monitor
from pikos.monitors.focused_function_monitor import FocusedFunctionMonitor
from pikos.recorders.list_recorder import ListRecorder
from pikos.tests.test_assistant import TestAssistant


class TestFocusedFunctionMonitor(unittest.TestCase, TestAssistant):

    def test_function(self):
        def gcd(x, y):
            while x > 0:
                x, y = internal(x, y)
            return y

        def internal(x, y):
            return y % x, x

        def boo():
            pass

        recorder = ListRecorder()
        logger = FocusedFunctionMonitor(recorder, [gcd])

        @monitor(logger)
        def container(x, y):
            boo()
            result = gcd(x, y)
            boo()
            return result

        boo()
        result = container(12, 3)
        boo()
        self.assertEqual(result, 3)
        records = recorder.records
        # check that the records make sense
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('internal', 'call'), times=2)
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('internal', 'return'), times=2)
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('gcd', 'call'), times=1)
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('gcd', 'return'), times=1)
        self.assertFieldValueNotExist(records, ('function',), ('boo',))
        self.assertFieldValueNotExist(records, ('function',), ('container',))
        # The wrapper of the function should not be logged
        self.assertFieldValueNotExist(records, ('function',), ('wrapper',))


if __name__ == '__main__':
    unittest.main()
