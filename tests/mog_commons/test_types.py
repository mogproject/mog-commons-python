# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import six
from mog_commons import unittest
from mog_commons.types import *
from mog_commons.types import _get_name


class TestTypes(unittest.TestCase):
    @staticmethod
    @types(int, x=int, y=int)
    def bin_func(x, y):
        return x + y

    @staticmethod
    @types(p1=int, p2=ListOf(int), p3=int, p4=String, p5=String, k=VarArg(ListOf(DictOf(String, SetOf(int)))),
           kw=KwArg(float))
    def complex_func(p1, p2, p3, p4='xxx', p5='yyy', *k, **kw):
        return 1

    @staticmethod
    @types(a=str)
    def err_func1(b):
        return b

    @staticmethod
    def err_func2():
        @types(bool, int)
        def f():
            pass
        return 1

    @staticmethod
    @types(bool)
    def predicate():
        return 1

    def test_types(self):
        str_type = '(basestring|str)' if six.PY2 else '(str|bytes)'

        self.assertEqual(self.bin_func(10, 20), 30)
        self.assertRaisesMessage(AssertionError, 'x must be int, not dict.', self.bin_func, {}, 20)
        self.assertRaisesMessage(AssertionError, 'y must be int, not list.', self.bin_func, 10, [])

        self.assertEqual(self.complex_func(123, [1, 2], 10, 'abc', 'def', [{'x': set([3, 4, 5])}]), 1)
        self.assertRaisesMessage(AssertionError, 'kw must be dict(%s->float), not dict.' % str_type,
                                 self.complex_func, 123, [1, 2], 10, 'abc', 'def', [{'x': set([3, 4, 5])}], x='12.3')

        self.assertRaisesMessage(AssertionError, 'must return bool, not int.', self.predicate)

    def test_types_error(self):
        self.assertRaisesMessage(AssertionError, 'Not found argument: a', self.err_func1, 123)
        self.assertRaisesMessage(AssertionError, 'You can specify at most one return type.', self.err_func2)

    def test_get_name(self):
        str_type = '(basestring|str)' if six.PY2 else '(str|bytes)'
        unicode_type = 'unicode' if six.PY2 else 'str'

        self.assertEqual(_get_name(int), 'int')
        self.assertEqual(_get_name(String), str_type)
        self.assertEqual(_get_name(Unicode), unicode_type)
        self.assertEqual(_get_name(TupleOf(int)), 'tuple(int)')
        self.assertEqual(_get_name(ListOf(int)), 'list(int)')
        self.assertEqual(_get_name(SetOf(int)), 'set(int)')
        self.assertEqual(_get_name(DictOf(int, float)), 'dict(int->float)')
        self.assertEqual(_get_name(VarArg(str)), 'tuple(str)')
        self.assertEqual(_get_name(KwArg(str)), 'dict(%s->str)' % str_type)
        self.assertEqual(_get_name(KwArg(ListOf(DictOf(float, SetOf((str, TupleOf(Unicode))))))),
                         'dict(%s->list(dict(float->set((str|tuple(%s))))))' % (str_type, unicode_type))
