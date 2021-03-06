# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
#  Package: Pikos toolkit
#  File: monitors/test_focused_function_monitor.py
#  License: LICENSE.TXT
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import unittest

from pikos.monitors.focused_function_monitor import FocusedFunctionMonitor
from pikos.recorders.list_recorder import ListRecorder
from pikos.monitors.function_monitor import FunctionRecord
from pikos.tests.test_assistant import TestAssistant
from pikos.tests.compat import TestCase


class TestFocusedFunctionMonitor(TestCase, TestAssistant):

    def setUp(self):
        self.filename = __file__.replace('.pyc', '.py')
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
        logger = FocusedFunctionMonitor(recorder, functions=[gcd])

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
                                   lineNo=27, filename=self.filename),
                    FunctionRecord(index=1, type='call', function='internal',
                                   lineNo=32, filename=self.filename),
                    FunctionRecord(index=2, type='call',
                                   function='boo', lineNo=36,
                                   filename=self.filename),
                    FunctionRecord(index=3, type='return',
                                   function='boo', lineNo=37,
                                   filename=self.filename),
                    FunctionRecord(index=4, type='return',
                                   function='internal', lineNo=34,
                                   filename=self.filename),
                    FunctionRecord(index=5, type='call', function='internal',
                                   lineNo=32, filename=self.filename),
                    FunctionRecord(index=6, type='call',
                                   function='boo', lineNo=36,
                                   filename=self.filename),
                    FunctionRecord(index=7, type='return',
                                   function='boo', lineNo=37,
                                   filename=self.filename),
                    FunctionRecord(index=8, type='return',
                                   function='internal', lineNo=34,
                                   filename=self.filename),
                    FunctionRecord(index=9, type='return', function='gcd',
                                   lineNo=30, filename=self.filename)]
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
        logger = FocusedFunctionMonitor(recorder, functions=[gcd, foo])

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
                                   lineNo=85, filename=self.filename),
                    FunctionRecord(index=1, type='call', function='internal',
                                   lineNo=90, filename=self.filename),
                    FunctionRecord(index=2, type='return',
                                   function='internal', lineNo=91,
                                   filename=self.filename),
                    FunctionRecord(index=3, type='call', function='internal',
                                   lineNo=90, filename=self.filename),
                    FunctionRecord(index=4, type='return',
                                   function='internal', lineNo=91,
                                   filename=self.filename),
                    FunctionRecord(index=5, type='return', function='gcd',
                                   lineNo=88, filename=self.filename),
                    FunctionRecord(index=6, type='call',
                                   function='foo', lineNo=96,
                                   filename=self.filename),
                    FunctionRecord(index=7, type='call',
                                   function='boo', lineNo=93,
                                   filename=self.filename),
                    FunctionRecord(index=8, type='return',
                                   function='boo', lineNo=94,
                                   filename=self.filename),
                    FunctionRecord(index=9, type='call',
                                   function='boo', lineNo=93,
                                   filename=self.filename),
                    FunctionRecord(index=10, type='return',
                                   function='boo', lineNo=94,
                                   filename=self.filename),
                    FunctionRecord(index=11, type='return',
                                   function='foo', lineNo=98,
                                   filename=self.filename), ]
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
        logger = FocusedFunctionMonitor(recorder, functions=[gcd])

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
                                   lineNo=153, filename=self.filename),
                    FunctionRecord(index=1, type='call', function='foo',
                                   lineNo=160, filename=self.filename),
                    FunctionRecord(index=2, type='return', function='foo',
                                   lineNo=161, filename=self.filename),
                    FunctionRecord(index=3, type='call', function='gcd',
                                   lineNo=153, filename=self.filename),
                    FunctionRecord(index=4, type='call', function='foo',
                                   lineNo=160, filename=self.filename),
                    FunctionRecord(index=5, type='return', function='foo',
                                   lineNo=161, filename=self.filename),
                    FunctionRecord(index=6, type='return', function='gcd',
                                   lineNo=155, filename=self.filename),
                    FunctionRecord(index=7, type='return', function='gcd',
                                   lineNo=155, filename=self.filename), ]
        self.assertEqual(records, expected)
        self.assertEqual(logger._code_trackers, {})


if __name__ == '__main__':
    unittest.main()
