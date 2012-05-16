import os
import StringIO
import unittest

from pikos.recorders.text_stream_recorder import TextStreamRecorder
from pikos.recorders.abstract_recorder import RecorderError

class TestTextStreamRecorder(unittest.TestCase):

    def setUp(self):
        self.temp = StringIO.StringIO()
        self.maxDiff = None

    def tearDown(self):
        self.temp.close()

    def test_prepare(self):
        fields = ('one', 'two','three')
        header = '{:<30} {:<30} {:<30}{newline}{:-<{length}}{newline}'.\
                 format('one', 'two', 'three', '', newline=os.linesep,
                       length=92)
        recorder = TextStreamRecorder(self.temp)
        recorder.prepare(fields)

        # the first call writes the header
        self.assertMultiLineEqual(self.temp.getvalue(), header)
        recorder.prepare(fields)
        # all calls after that do nothing
        for x in range(10):
            recorder.prepare(fields)
        self.assertMultiLineEqual(self.temp.getvalue(), header)

    def test_finalize(self):
        fields = ('one', 'two','three')
        header = '{:<30} {:<30} {:<30}{newline}{:-<{length}}{newline}'.\
                 format('one', 'two', 'three', '', newline=os.linesep,
                       length=92)
        recorder = TextStreamRecorder(self.temp)
        # all calls do nothing
        recorder.prepare(fields)
        for x in range(10):
            recorder.finalize()
        self.assertMultiLineEqual(self.temp.getvalue(), header)

    def test_record(self):
        fields = ('one', 'two','three')
        values = (5, 'pikos','apikos')
        output = ('{:<30} {:<30} {:<30}{newline}'
                  '{:-<{length}}{newline}'
                  '{:<30} {:<30} {:<30}{newline}'.\
                  format('one', 'two', 'three', '', 5, 'pikos', 'apikos',
                        newline=os.linesep, length=92))
        recorder = TextStreamRecorder(self.temp)
        recorder.prepare(fields)
        recorder.record(values)
        self.assertMultiLineEqual(self.temp.getvalue(), output)

    def test_filter(self):
        fields = ('one', 'two','three')
        values = [(5, 'pikos','apikos'), (12, 'emilios','milo')]
        output = ('{:<30} {:<30} {:<30}{newline}'
                  '{:-<{length}}{newline}'
                  '{:<30} {:<30} {:<30}{newline}'.\
                  format('one', 'two', 'three', '', 12, 'emilios', 'milo',
                        newline=os.linesep, length=92))
        def not_pikos(values):
            return not 'pikos' in values
        recorder = TextStreamRecorder(self.temp, filter_=not_pikos)
        recorder.prepare(fields)
        for record in values:
            recorder.record(record)
        self.assertMultiLineEqual(self.temp.getvalue(), output)

    def test_exceptions(self):
        fields = ('one', 'two','three')
        values = [(5, 'pikos','apikos')]
        recorder = TextStreamRecorder(self.temp)

        with self.assertRaises(RecorderError):
            recorder.record(values)

        with self.assertRaises(RecorderError):
            recorder.finalize()

if __name__ == '__main__':
    unittest.main()
