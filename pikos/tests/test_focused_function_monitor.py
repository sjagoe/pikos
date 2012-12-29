import os
import unittest

from pikos.monitors.focused_function_monitor import FocusedFunctionMonitor
from pikos.recorders.list_recorder import ListRecorder
from pikos.monitors.function_monitor import FunctionRecord
from pikos.tests.test_assistant import TestAssistant


class TestFocusedFunctionMonitor(unittest.TestCase, TestAssistant):

    def setUp(self):
        self.filename = __file__
        self.maxDiff = None

    def test_focus_on_function(self):

        def gcd(x, y):
            while x > 0:
                x, y = internal(x, y)
            return y

        def internal(x, y):
            boo()
            return y % x, x

        def boo():
            pass

        recorder = ListRecorder()
        logger = FocusedFunctionMonitor(recorder, [gcd])

        @logger.attach
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
        expected = [FunctionRecord(index=0, type='call', function='gcd',
                                   lineNo=18, filename=self.filename),
                    FunctionRecord(index=1, type='call', function='internal',
                                   lineNo=23, filename=self.filename),
                    FunctionRecord(index=2, type='call',
                                   function='boo', lineNo=27,
                                   filename=self.filename),
                    FunctionRecord(index=3, type='return',
                                   function='boo', lineNo=28,
                                   filename=self.filename),
                    FunctionRecord(index=4, type='return',
                                   function='internal', lineNo=25,
                                   filename=self.filename),
                    FunctionRecord(index=5, type='call', function='internal',
                                   lineNo=23, filename=self.filename),
                    FunctionRecord(index=6, type='call',
                                   function='boo', lineNo=27,
                                   filename=self.filename),
                    FunctionRecord(index=7, type='return',
                                   function='boo', lineNo=28,
                                   filename=self.filename),
                    FunctionRecord(index=8, type='return',
                                   function='internal', lineNo=25,
                                   filename=self.filename),
                    FunctionRecord(index=9, type='return', function='gcd',
                                   lineNo=21, filename=self.filename)]
        self.assertEqual(records, expected)
        self.assertEqual(logger._code_trackers, {})

    def test_focus_on_functions(self):

        def gcd(x, y):
            while x > 0:
                x, y = internal(x, y)
            return y

        def internal(x, y):
            return y % x, x

        def boo():
            pass

        def foo():
            boo()
            boo()

        recorder = ListRecorder()
        logger = FocusedFunctionMonitor(recorder, [gcd, foo])

        @logger.attach
        def container(x, y):
            boo()
            result = gcd(x, y)
            boo()
            foo()
            return result

        boo()
        result = container(12, 3)
        boo()
        self.assertEqual(result, 3)
        records = recorder.records
        expected = [FunctionRecord(index=0, type='call', function='gcd',
                                   lineNo=76, filename=self.filename),
                    FunctionRecord(index=1, type='call', function='internal',
                                   lineNo=81, filename=self.filename),
                    FunctionRecord(index=2, type='return',
                                   function='internal', lineNo=82,
                                   filename=self.filename),
                    FunctionRecord(index=3, type='call', function='internal',
                                   lineNo=81, filename=self.filename),
                    FunctionRecord(index=4, type='return',
                                   function='internal', lineNo=82,
                                   filename=self.filename),
                    FunctionRecord(index=5, type='return', function='gcd',
                                   lineNo=79, filename=self.filename),
                    FunctionRecord(index=6, type='call',
                                   function='foo', lineNo=87,
                                   filename=self.filename),
                    FunctionRecord(index=7, type='call',
                                   function='boo', lineNo=84,
                                   filename=self.filename),
                    FunctionRecord(index=8, type='return',
                                   function='boo', lineNo=85,
                                   filename=self.filename),
                    FunctionRecord(index=9, type='call',
                                   function='boo', lineNo=84,
                                   filename=self.filename),
                    FunctionRecord(index=10, type='return',
                                   function='boo', lineNo=85,
                                   filename=self.filename),
                    FunctionRecord(index=11, type='return',
                                   function='foo', lineNo=89,
                                   filename=self.filename),]
        self.assertEqual(records, expected)
        self.assertEqual(logger._code_trackers, {})

    def test_focus_on_recursive(self):

        def gcd(x, y):
            foo()
            return x if y == 0 else gcd(y, (x % y))

        def boo():
            pass

        def foo():
            pass

        recorder = ListRecorder()
        logger = FocusedFunctionMonitor(recorder, [gcd])

        @logger.attach
        def container(x, y):
            boo()
            result = gcd(x, y)
            boo()
            foo()
            return result

        boo()
        result = container(12, 3)
        boo()
        self.assertEqual(result, 3)
        records = recorder.records
        expected = [FunctionRecord(index=0, type='call', function='gcd',
                                   lineNo=144, filename=self.filename),
                    FunctionRecord(index=1, type='call', function='foo',
                                   lineNo=151, filename=self.filename),
                    FunctionRecord(index=2, type='return', function='foo',
                                   lineNo=152, filename=self.filename),
                    FunctionRecord(index=3, type='call', function='gcd',
                                   lineNo=144, filename=self.filename),
                    FunctionRecord(index=4, type='call', function='foo',
                                   lineNo=151, filename=self.filename),
                    FunctionRecord(index=5, type='return', function='foo',
                                   lineNo=152, filename=self.filename),
                    FunctionRecord(index=6, type='return', function='gcd',
                                   lineNo=146, filename=self.filename),
                    FunctionRecord(index=7, type='return', function='gcd',
                                   lineNo=146, filename=self.filename),]
        self.assertEqual(records, expected)
        self.assertEqual(logger._code_trackers, {})


if __name__ == '__main__':
    unittest.main()
