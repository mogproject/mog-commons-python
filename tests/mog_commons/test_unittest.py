from __future__ import division, print_function, absolute_import, unicode_literals

import sys
from mog_commons import unittest


class TestUnitTest(unittest.TestCase):
    def test_assert_output(self):
        def f():
            print('abc')
            print('123')
            sys.stderr.writelines(['def\n', '456\n'])
        self.assertOutput('abc\n123\n', 'def\n456\n', f)

    def test_assert_output_fail(self):
        def f():
            print('abc')
            print('123')
            sys.stderr.writelines(['def\n', '456\n'])
        self.assertRaisesRegexp(AssertionError, 'abc.+ != ', self.assertOutput, '', 'def\n456\n', f)
        self.assertRaisesRegexp(AssertionError, 'def.+ != ', self.assertOutput, 'abc\n123\n', '', f)
        self.assertRaisesRegexp(AssertionError, 'def.+ != .+def', self.assertOutput, 'abc\n123\n', 'def\n456\n\n', f)

    def test_assert_system_exit(self):
        self.assertSystemExit(123, lambda: sys.exit(123))
        self.assertSystemExit(234, lambda x: sys.exit(x), 234)

    def test_assert_system_exit_fail(self):
        self.assertRaisesRegexp(AssertionError, 'SystemExit not raised', self.assertSystemExit, 0, lambda: 0)
        self.assertRaisesRegexp(AssertionError, '1 != 0', self.assertSystemExit, 0, lambda: sys.exit(1))
