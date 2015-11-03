# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import time
from mog_commons.terminal import TerminalHandler
from mog_commons.unittest import TestCase, base_unittest, FakeBytesInput


class TestTerminal(TestCase):
    def test_getch_from_file(self):
        with open(os.path.join('tests', 'resources', 'test_terminal_input.txt')) as f:
            t = TerminalHandler(stdin=f)
            self.assertEqual(t.getch(), 'a')
            self.assertRaises(EOFError, t.getch)

    @base_unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
    def test_getch(self):
        self.assertEqual(TerminalHandler(stdin=FakeBytesInput(b'')).getch(), '')
        self.assertEqual(TerminalHandler(stdin=FakeBytesInput(b'\x03')).getch(), '\x03')
        self.assertEqual(TerminalHandler(stdin=FakeBytesInput(b'abc')).getch(), 'a')
        self.assertEqual(TerminalHandler(stdin=FakeBytesInput('あ'.encode('utf-8'))).getch(), '')
        self.assertEqual(TerminalHandler(stdin=FakeBytesInput('あ'.encode('sjis'))).getch(), '')

    @base_unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
    def test_getch_key_repeat(self):
        fin = FakeBytesInput(b'abcde')
        t = TerminalHandler(stdin=fin)

        def append_char(ch):
            fin.write(ch)
            fin.seek(-len(ch), 1)

        self.assertEqual(t.getch(), 'a')
        append_char(b'x')
        self.assertEqual(t.getch(), 'x')
        append_char(b'x')
        self.assertEqual(t.getch(), '')
        append_char(b'y')
        self.assertEqual(t.getch(), 'y')
        append_char(b'y')
        self.assertEqual(t.getch(), '')

        time.sleep(1)
        append_char(b'y')
        self.assertEqual(t.getch(), 'y')
