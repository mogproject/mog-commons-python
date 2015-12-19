from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import six
import io
import tempfile
from contextlib import contextmanager
import jinja2

# unittest
if sys.version_info < (2, 7):
    import unittest2 as base_unittest
else:
    import unittest as base_unittest

from mog_commons.string import to_bytes, to_str
from mog_commons.types import *

__all__ = [
    'FakeInput',
    'FakeBytesInput',
    'TestCase',
]


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


class BytesBuffer(six.BytesIO):
    """
    Replace for six.BytesIO

    More strict type checking and implicit conversion of unicode to bytes are implemented.
    """

    @types(s=String)
    def write(self, s, encoding='utf-8', errors='strict'):
        six.BytesIO.write(self, to_bytes(s, encoding, errors))


class FakeInput(six.StringIO):
    """Fake input object"""

    def __init__(self, buff=None):
        six.StringIO.__init__(self, buff or '')

    def fileno(self):
        return 0

    def isatty(self):
        return True


class FakeBytesInput(six.BytesIO):
    """Fake bytes input object"""

    def __init__(self, buff=None):
        six.BytesIO.__init__(self, buff or b'')

    def fileno(self):
        return 0

    def isatty(self):
        return True


class TestCase(base_unittest.TestCase):
    def assertRaisesRegexp(self, expected_exception, expected_regexp, callable_obj=None, *args, **kwargs):
        """
        Accept difference of the function name between PY2 and PY3.

        We don't use built-in assertRaisesRegexp because it is unicode-unsafe.
        """
        encoding = 'utf-8'
        with self.assertRaises(expected_exception) as cm:
            callable_obj(*args, **kwargs)
        if six.PY2:
            try:
                msg = to_str(cm.exception, encoding)
            except UnicodeEncodeError:
                # avoid to use cm.exception.message
                msg = cm.exception.args[0]
            self.assertRegexpMatches(msg, expected_regexp)
        else:
            self.assertRegex(to_str(cm.exception, encoding), expected_regexp)

    def assertRaisesMessage(self, expected_exception, expected_message, callable_obj=None, *args, **kwargs):
        """
        Assert the expected exception is raised and its message is equal to expected.

        :param expected_exception: class:
        :param expected_message: string:
        :param callable_obj: function:
        :param args: args
        :param kwargs: kwargs
        """
        encoding = 'utf-8'
        with self.assertRaises(expected_exception) as cm:
            callable_obj(*args, **kwargs)
        try:
            msg = to_str(cm.exception, encoding)
        except UnicodeEncodeError:
            # avoid to use cm.exception.message
            msg = cm.exception.args[0]
        self.assertEqual(msg, expected_message)

    @contextmanager
    def withOutput(self, buffer_type=StringBuffer):
        """
        Capture and suppress stdout and stderr.
        example:
            with self.withOutput() as (out, err):
                (do main logic)
            (verify out.getvalue() or err.getvalue())
        """
        new_out, new_err = buffer_type(), buffer_type()
        old_out, old_err = sys.stdout, sys.stderr

        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    @contextmanager
    def withBytesOutput(self):
        """
        Capture and suppress stdout and stderr. The value is represented as bytes.
        example:
            with self.withBytesOutput() as (out, err):
                (do main logic)
            (verify out.getvalue() or err.getvalue())
        """
        with self.withOutput(BytesBuffer) as (out, err):
            yield out, err

    @contextmanager
    def withAssertOutput(self, expected_stdout, expected_stderr, encoding='utf-8'):
        with self.withOutput() as (out, err):
            yield out, err
        self.assertMultiLineEqual(out.getvalue(encoding), expected_stdout)
        self.assertMultiLineEqual(err.getvalue(encoding), expected_stderr)

    def assertOutput(self, expected_stdout, expected_stderr, function, encoding='utf-8'):
        with self.withAssertOutput(expected_stdout, expected_stderr, encoding) as (out, err):
            function()

    @contextmanager
    def withAssertOutputFile(self, expect_file, variables=None, expect_file_encoding='utf-8', output_encoding='utf-8',
                             replace_linesep=False):
        """
        Create a temporary file as output and compare with the file content.

        :param expect_file: string: path to the file which contains the expected output
        :param variables: dict: variables for template engine jinja2
        :param expect_file_encoding: string:
        :param output_encoding: string:
        :param replace_linesep: replace all newlines in the expected file to OS default separator if true
        """
        with tempfile.TemporaryFile() as out:
            yield out

            with io.open(expect_file, encoding=expect_file_encoding) as f:
                expect = f.read()
                if variables:
                    expect = jinja2.Template(expect).render(**variables)
                if replace_linesep:
                    expect = expect.replace('\n', os.linesep)

            out.seek(0)
            actual = out.read().decode(output_encoding)
            self.assertMultiLineEqual(actual, expect)

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
