# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import sys
from mog_commons import io, unittest


class TestIO(unittest.TestCase):
    def test_print_safe(self):
        self.assertOutput('あいう\n', '',
                          lambda: io.print_safe('あいう', output=sys.stdout))
        self.assertOutput('あいう\n', '',
                          lambda: io.print_safe('あいう', encoding='sjis', output=sys.stdout), 'sjis')

        # When a character failed to encode, it will be ignored.
        self.assertOutput('\n', '',
                          lambda: io.print_safe('あいう', encoding='ascii', output=sys.stdout))

        # When the string is already bytes, decode then encode with the specific encoding.
        self.assertOutput('あいう\n', '',
                          lambda: io.print_safe('あいう'.encode('utf-8'), encoding='utf-8', output=sys.stdout))
        self.assertOutput('\n', '',
                          lambda: io.print_safe('あいう'.encode('sjis'), encoding='utf-8', output=sys.stdout),
                          'sjis')
        self.assertOutput('\n', '',
                          lambda: io.print_safe('あいう'.encode('utf-8'), encoding='ascii', output=sys.stdout))
        self.assertOutput('あいう\n', '',
                          lambda: io.print_safe('あいう'.encode('sjis'), encoding='sjis', output=sys.stdout),
                          'sjis')
        self.assertOutput('\n', '',
                          lambda: io.print_safe('あいう'.encode('sjis'), encoding='ascii', output=sys.stdout),
                          'sjis')

    def test_print_safe_error(self):
        self.assertRaisesRegexp(UnicodeEncodeError,
                                "'ascii' codec can't encode characters in position 0-2: ordinal not in range\(128\)",
                                lambda: io.print_safe('あいう', encoding='ascii', output=sys.stdout, errors='strict'))
