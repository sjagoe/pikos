import StringIO
import unittest

from pikos.monitor import monitor
from pikos.loggers.function_logger import FunctionLogger
from pikos.recorders.list_recorder import ListRecorder
from pikos.recorders.text_stream_recorder import TextStreamRecorder

class TestFunctionLogger(unittest.TestCase):

    def test_function(self):
        recorder = ListRecorder()
        logger = FunctionLogger(recorder)

        @monitor(logger)
        def gcd(x,y):
            while x > 0:
                x, y = y % x, x
            return y

        def boo():
            pass

        boo()
        result = gcd(12, 3)
        boo()
        self.assertEqual(result, 3)
        records = recorder.records
        # check that the records make sense
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('gcd', 'call'), times=1)
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('gcd', 'return'), times=1)
        self.assertFieldValueNotExist(records, ('function',), ('boo',))
        # The wrapper of the function should not be logged
        self.assertFieldValueNotExist(records, ('function',), ('wrapper',))

    def test_recursive(self):
        recorder = ListRecorder()
        logger = FunctionLogger(recorder)

        @monitor(logger)
        def gcd(x,y):
            return x if y == 0 else gcd(y, (x % y))

        def boo():
            return gcd(7,12)

        result = boo()
        self.assertEqual(result, 1)
        records = recorder.records
        # check that the records make sense
        # The function should be called 6 times
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('gcd', 'call'), times=6)
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('gcd', 'return'), times=6)
        self.assertFieldValueNotExist(records, ('function',), ('boo',))
        # In recursive calls the wrapper of the function is logged
        # self.assertFieldValueNotExist(records, ('function',), ('wrapper',))

    def test_generator(self):
        recorder = ListRecorder()
        logger = FunctionLogger(recorder)
        output = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34)

        @monitor(logger)
        def fibonacci(items):
            x, y = 0, 1
            for i in range(items):
                yield x
                x, y = y, x + y

        def boo():
            pass

        boo()
        result = [value for value in fibonacci(10)]
        boo()
        self.assertSequenceEqual(result, output)
        records = recorder.records
        # check that the records make sense
        # The function should be called 10 + 1 times
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('fibonacci', 'call'), times=11)
        self.assertFieldValueExist(records, ('function', 'type'),
                                   ('fibonacci', 'return'), times=11)
        self.assertFieldValueNotExist(records, ('function',), ('boo',))
        # The wrapper of the generator should not be logged
        self.assertFieldValueNotExist(records, ('function',), ('wrapper',))

    def assertFieldValueExist(self, records, fields, values, times=None,
                              msg=None):
        """ Assert that the records containt a specific set of field entries.

        Parameters
        ----------
        records : iterateable
            An iterateable of records entrys to check.

        fields : list
            List of field names to look into

        value : tuple
            The corresponding value(s) to match over the fields of each entry.

        times : int
            The number of times that the value should be present in the fields.
            Default is to any number of times (i.e. None).

        msg : str
            overide the default assertion message.

        """
        count = 0
        for entry in records:
            data = [getattr(entry, field) for field in fields]
            if all(item == value for item, value in zip(data, values)):
                count += 1
        if times is None:
            msg = 'The value set {} could not be found in hte records'.\
                  format(zip(fields, values))
            self.assertGreater(count, 0, msg=msg)
        else:
            msg = ('The value set {} was found {} and not {} times in the'
                   'records.'.format(zip(fields, values), count, times))
            self.assertEqual(count, times, msg=msg)

    def assertFieldValueNotExist(self, records, fields, values):
        msg = 'The value set {} was unexpectedly found in the records'.\
              format(zip(fields, values))
        self.assertFieldValueExist(records, fields, values, times=0, msg=msg)

if __name__ == '__main__':
    unittest.main()
