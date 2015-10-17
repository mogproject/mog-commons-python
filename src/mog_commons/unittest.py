from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import six
from contextlib import contextmanager

# unittest
if sys.version_info < (2, 7):
    import unittest2 as base_unittest
else:
    import unittest as base_unittest

from mog_commons.string import to_bytes


class StringBuffer(object):
    """
    Replace for six.StringIO

    We don't use StringIO because there are many differences between PY2 and PY3.
    """
    def __init__(self, init_buffer=None):
        self._buffer = init_buffer or b''

    def write(self, s, encoding='utf-8', errors='strict'):
        self._buffer += to_bytes(s, encoding, errors)

    def writelines(self, lines, encoding='utf-8', errors='strict'):
        self._buffer += b''.join(to_bytes(s, encoding, errors) for s in lines)

    def flush(self):
        """do nothing"""

    def getvalue(self, encoding='utf-8', errors='strict'):
        return self._buffer.decode(encoding, errors)


class TestCase(base_unittest.TestCase):
    def assertRaisesRegexp(self, expected_exception, expected_regexp, callable_obj=None, *args, **kwargs):
        """Accept difference of the function name between PY2 and PY3."""
        f = base_unittest.TestCase.assertRaisesRegex if six.PY3 else base_unittest.TestCase.assertRaisesRegexp
        f(self, expected_exception, expected_regexp, callable_obj, *args, **kwargs)

    def assertOutput(self, expected_stdout, expected_stderr, function, encoding='utf-8'):
        with self.withOutput() as (out, err):
            function()
        self.assertMultiLineEqual(out.getvalue(encoding), expected_stdout)
        self.assertMultiLineEqual(err.getvalue(encoding), expected_stderr)

    @contextmanager
    def withOutput(self):
        """
        Capture and suppress stdout and stderr.
        example:
            with captured_output() as (out, err):
                (do main logic)
            (verify out.getvalue() or err.getvalue())
        """
        new_out, new_err = StringBuffer(), StringBuffer()
        old_out, old_err = sys.stdout, sys.stderr

        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def assertSystemExit(self, expected_code, callable_obj=None, *args, **kwargs):
        """
        Fail unless SystemExit is raised by callableObj when invoked with arguments args and keyword arguments kwargs.
        :param expect_code:
        :param function:
        :return:
        """
        with self.assertRaises(SystemExit) as cm:
            callable_obj(*args, **kwargs)
        actual_code = cm.exception if isinstance(cm.exception, int) else cm.exception.code
        self.assertEqual(actual_code, expected_code)
