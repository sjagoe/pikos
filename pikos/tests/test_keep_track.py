import unittest

from pikos._internal.keep_track import KeepTrack


class TestKeepTrack(unittest.TestCase):

    def test_lifetime(self):
        my_class = KeepTrack()
        self.assertTrue(my_class())
        self.assertFalse(my_class('setup'))
        self.assertFalse(my_class('setup'))
        self.assertFalse(my_class('teardown'))
        self.assertFalse(my_class('teardown'))
        self.assertTrue(my_class('teardown'))
        self.assertTrue(my_class('setup'))
        self.assertFalse(my_class('setup'))
        self.assertFalse(my_class('teardown'))
        self.assertTrue(my_class('teardown'))
        self.assertFalse(my_class('teardown'))
        self.assertTrue(my_class())


if __name__ == '__main__':
    unittest.main()
