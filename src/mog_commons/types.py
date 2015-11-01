from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import six
from abc import ABCMeta, abstractmethod

if sys.version_info < (2, 7):
    from mog_commons.backported.inspect2 import getcallargs
else:
    from inspect import getcallargs

__all__ = [
    'String',
    'Unicode',
    'Option',
    'ListOf',
    'TupleOf',
    'SetOf',
    'DictOf',
    'VarArg',
    'KwArg',
    'types',
]

#
# Type definitions
#
String = six.string_types + (bytes,)

Unicode = unicode if six.PY2 else str


@six.add_metaclass(ABCMeta)
class ComposableType(object):
    """Label for composable types"""

    @abstractmethod
    def name(self):
        """abstract method"""

    @abstractmethod
    def check(self, obj):
        """abstract method"""


@six.add_metaclass(ABCMeta)
class IterableOf(ComposableType):
    def __init__(self, iterable_type, elem_type):
        self.iterable_type = iterable_type
        self.elem_type = elem_type

    def name(self):
        return '%s(%s)' % (self.iterable_type.__name__, _get_name(self.elem_type))

    def check(self, obj):
        return isinstance(obj, self.iterable_type) and all(_check_type(elem, self.elem_type) for elem in obj)


class ListOf(IterableOf):
    """Label for list element type assertion"""

    def __init__(self, elem_type):
        IterableOf.__init__(self, list, elem_type)


class TupleOf(IterableOf):
    """Label for tuple element type assertion"""

    def __init__(self, elem_type):
        IterableOf.__init__(self, tuple, elem_type)


class SetOf(IterableOf):
    """Label for set element type assertion"""

    def __init__(self, elem_type):
        IterableOf.__init__(self, set, elem_type)


class DictOf(ComposableType):
    """Label for dict element type assertion"""

    def __init__(self, key_type, value_type):
        self.key_type = key_type
        self.value_type = value_type

    def name(self):
        return 'dict(%s->%s)' % (_get_name(self.key_type), _get_name(self.value_type))

    def check(self, obj):
        return isinstance(obj, dict) and all(
            _check_type(k, self.key_type) and _check_type(v, self.value_type) for k, v in obj.items())


def VarArg(cls):
    """Shorthand description for var arg"""
    return TupleOf(cls)


def KwArg(cls):
    """Shorthand description for keyword arg"""
    return DictOf(String, cls)


def Option(cls):
    """Shorthand description for a type allowing NoneType"""
    return cls + (type(None),) if isinstance(cls, tuple) else (cls, type(None))


#
# Helper functions
#
def _get_name(cls):
    if isinstance(cls, ComposableType):
        return cls.name()
    if isinstance(cls, tuple):
        return '(%s)' % '|'.join(_get_name(t) for t in cls)
    else:
        return cls.__name__


def _check_type(obj, cls):
    if isinstance(cls, ComposableType):
        return cls.check(obj)
    elif isinstance(cls, tuple):
        return any(_check_type(obj, t) for t in cls)
    else:
        return isinstance(obj, cls)


#
# Decorators
#
def types(*return_type, **arg_types):
    """
    Assert types of the function arguments and return value.
    :param return_type: expected type of the return value
    :param arg_types: expected types of the arguments

    :example:
    @types(float, x=int, y=float, z=ListOf(int))
    def f(x, y, z):
        return x * y + sum(z)
    """
    assert len(return_type) <= 1, 'You can specify at most one return type.'

    arg_msg = '%s must be %s, not %s.'
    return_msg = 'must return %s, not %s.'

    def f(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # convert args to call args
            call_args = getcallargs(func, *args, **kwargs)

            for arg_name, expect in arg_types.items():
                assert arg_name in call_args, 'Not found argument: %s' % arg_name
                actual = call_args[arg_name]
                if not _check_type(actual, expect):
                    raise TypeError(arg_msg % (arg_name, _get_name(expect), type(actual).__name__))

            ret = func(*args, **kwargs)
            if return_type:
                if not _check_type(ret, return_type[0]):
                    raise TypeError(return_msg % (_get_name(return_type[0]), type(ret).__name__))
            return ret

        return wrapper

    return f
