# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import six
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

    def test_with_bytes_output(self):
        with self.withBytesOutput() as (out, err):
            out.write(b'\xff\xfe')
            out.write('あいうえお'.encode('utf-8'))
            err.write(b'\xfd\xfc')
        self.assertEqual(out.getvalue(), b'\xff\xfe' + 'あいうえお'.encode('utf-8'))
        self.assertEqual(err.getvalue(), b'\xfd\xfc')

    def test_with_assert_output_file(self):
        def f(text):
            with self.withAssertOutputFile(os.path.join('tests', 'resources', 'utf8_ja.txt')) as out:
                out.write(text.encode('utf-8'))

        def g(text):
            with self.withAssertOutputFile(
                os.path.join('tests', 'resources', 'utf8_ja_template.txt'), {'text': 'かきくけこ'}
            ) as out:
                out.write(text.encode('utf-8'))

        f('あいうえお\n')
        self.assertRaisesRegexp(AssertionError, 'あいうえお', f, 'あいうえお')

        g('かきくけこ\n')
        self.assertRaisesRegexp(AssertionError, 'かきくけこ', g, 'あいうえお\n')

    def test_assert_raises_message(self):
        class MyException(Exception):
            pass

        def f(msg):
            raise MyException(msg)

        self.assertRaisesMessage(MyException, 'あいうえお', f, 'あいうえお')
        self.assertRaisesMessage(AssertionError, 'MyException not raised',
                                 self.assertRaisesMessage, MyException, 'あいうえお', lambda: None)

        if six.PY2:
            expected = ("u'\\u3042\\u3044\\u3046\\u3048' != u'\\u3042\\u3044\\u3046\\u3048\\u304a'\n" +
                        "- \u3042\u3044\u3046\u3048\n+ \u3042\u3044\u3046\u3048\u304a\n?     +\n")
        else:
            expected = "'あいうえ' != 'あいうえお'\n- あいうえ\n+ あいうえお\n?     +\n"
        self.assertRaisesMessage(AssertionError, expected,
                                 self.assertRaisesMessage, MyException, 'あいうえお', f, 'あいうえ')

    def test_assert_system_exit_fail(self):
        self.assertRaisesRegexp(AssertionError, 'SystemExit not raised', self.assertSystemExit, 0, lambda: 0)
        self.assertRaisesRegexp(AssertionError, '1 != 0', self.assertSystemExit, 0, lambda: sys.exit(1))
