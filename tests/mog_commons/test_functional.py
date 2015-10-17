from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.functional import omap, oget, ozip
from mog_commons import unittest


class TestFunctional(unittest.TestCase):
    def test_omap(self):
        self.assertEqual(omap(lambda x: x + 1, 123), 124)
        self.assertEqual(omap(lambda x: x + 1, None), None)

    def test_oget(self):
        self.assertEqual(oget(123), 123)
        self.assertEqual(oget(None), None)
        self.assertEqual(oget(123, 45), 123)
        self.assertEqual(oget(None, 45), 45)

    def test_ozip(self):
        self.assertEqual(ozip(), ())

        self.assertEqual(ozip(None, None), None)
        self.assertEqual(ozip(None, 45), None)
        self.assertEqual(ozip(123, None), None)
        self.assertEqual(ozip(123, 45), (123, 45))

        self.assertEqual(ozip(None, None, None), None)
        self.assertEqual(ozip(None, 45, None), None)
        self.assertEqual(ozip(123, 45, 67), (123, 45, 67))
