from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import six
from contextlib import contextmanager

# unittest
if sys.version_info < (2, 7):
    import unittest2 as base_unittest
else:
    import unittest as base_unittest


class TestCase(base_unittest.TestCase):
    def assertRaisesRegexp(self, expected_exception, expected_regexp, callable_obj=None, *args, **kwargs):
        """Accept difference of the function name between PY2 and PY3."""
        f = base_unittest.TestCase.assertRaisesRegex if six.PY3 else base_unittest.TestCase.assertRaisesRegexp
        f(self, expected_exception, expected_regexp, callable_obj, *args, **kwargs)

    def assertOutput(self, expected_stdout, expected_stderr, function):
        with self.withOutput() as (out, err):
            function()
        self.assertMultiLineEqual(out.getvalue(), expected_stdout)
        self.assertMultiLineEqual(err.getvalue(), expected_stderr)

    @contextmanager
    def withOutput(self):
        """
        Capture and suppress stdout and stderr.
        example:
            with captured_output() as (out, err):
                (do main logic)
            (verify out.getvalue() or err.getvalue())
        """
        new_out, new_err = six.StringIO(), six.StringIO()
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
