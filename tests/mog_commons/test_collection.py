from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.collection import get_single_item, get_single_key, get_single_value
from mog_commons import unittest


class TestCollection(unittest.TestCase):
    def test_get_single_item(self):
        self.assertEqual(get_single_item({'x': 123}), ('x', 123))

    def test_get_single_item_error(self):
        self.assertRaisesRegexp(AssertionError, 'Single-item dict must have just one item, not 0.', get_single_item,
                                {})
        self.assertRaisesRegexp(AssertionError, 'Single-item dict must have just one item, not 2.', get_single_item,
                                {'x': 123, 'y': 45})

    def test_get_single_key(self):
        self.assertEqual(get_single_key({'x': 123}), 'x')

    def test_get_single_key_error(self):
        self.assertRaisesRegexp(AssertionError, 'Single-item dict must have just one item, not 0.', get_single_key,
                                {})
        self.assertRaisesRegexp(AssertionError, 'Single-item dict must have just one item, not 2.', get_single_key,
                                {'x': 123, 'y': 45})

    def test_get_single_value(self):
        self.assertEqual(get_single_value({'x': 123}), 123)

    def test_get_single_value_error(self):
        self.assertRaisesRegexp(AssertionError, 'Single-item dict must have just one item, not 0.', get_single_value,
                                {})
        self.assertRaisesRegexp(AssertionError, 'Single-item dict must have just one item, not 2.', get_single_value,
                                {'x': 123, 'y': 45})
