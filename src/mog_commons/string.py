from __future__ import division, print_function, absolute_import, unicode_literals

from unicodedata import east_asian_width
import six

from mog_commons.collection import distinct
from mog_commons.types import *

__all__ = [
    'is_unicode',
    'is_strlike',
    'unicode_width',
    'to_unicode',
    'to_str',
    'to_bytes',
    'edge_just',
    'unicode_ljust',
    'unicode_rjust',
    'unicode_right',
    'unicode_left',
    'unicode_decode',
]

__unicode_width_mapping = {'F': 2, 'H': 1, 'W': 2, 'Na': 1, 'A': 2, 'N': 1}


def is_unicode(s):
    return (six.PY2 and isinstance(s, unicode)) or (six.PY3 and isinstance(s, str))


def is_strlike(s):
    return isinstance(s, (six.string_types, bytes))


@types(s=String)
def unicode_width(s):
    if is_unicode(s):
        return sum(__unicode_width_mapping[east_asian_width(c)] for c in s)

    assert is_strlike(s), 's must be a string, not %s.' % type(s).__name__
    return len(s)


@types(encoding=Option(String), errors=String)
def to_unicode(s, encoding=None, errors='strict'):
    """
    Make unicode string from any value
    :param s:
    :param encoding:
    :param errors:
    :return: unicode
    """
    encoding = encoding or 'utf-8'

    if is_unicode(s):
        return s
    elif is_strlike(s):
        return s.decode(encoding, errors)
    else:
        if six.PY2:
            return str(s).decode(encoding, errors)
        else:
            return str(s)


@types(encoding=Option(String), errors=String)
def to_str(s, encoding=None, errors='strict'):
    """
    Make str from any value
    :param s:
    :param encoding:
    :param errors:
    :return: str (not unicode in Python2, nor bytes in Python3)
    """
    encoding = encoding or 'utf-8'

    if is_strlike(s):
        if six.PY2:
            return s.encode(encoding, errors) if isinstance(s, unicode) else s
        else:
            return s.decode(encoding, errors) if isinstance(s, bytes) else s
    else:
        return str(s)


@types(encoding=Option(String), errors=String)
def to_bytes(s, encoding=None, errors='strict'):
    """Convert string to bytes."""
    encoding = encoding or 'utf-8'

    if is_unicode(s):
        return s.encode(encoding, errors)
    elif is_strlike(s):
        return s
    else:
        if six.PY2:
            return str(s)
        else:
            return str(s).encode(encoding, errors)


@types(left=String, right=String, width=int, fillchar=String, min_padding_length=int)
def edge_just(left, right, width, fillchar=' ', min_padding_length=1):
    """
    :param left:
    :param right:
    :param width:
    :param fillchar:
    :param min_padding_length: minimum padding length
    :return:
    """
    assert unicode_width(fillchar) == 1, 'fillchar must be single-width char'
    padding = fillchar * max(min_padding_length, width - unicode_width(left + right))
    return left + padding + right


@types(s=String, width=int, fillchar=String)
def unicode_ljust(s, width, fillchar=' '):
    """
    Return Unicode string left-justified in a print-length width.
    Padding is done using the specified fill character (default is a space).
    """
    return edge_just(s, '', width, fillchar, 0)


@types(s=String, width=int, fillchar=String)
def unicode_rjust(s, width, fillchar=' '):
    """
    Return Unicode string right-justified in a print-length width.
    Padding is done using the specified fill character (default is a space).
    """
    return edge_just('', s, width, fillchar, 0)


@types(s=String, width=int)
def unicode_left(s, width):
    """Cut unicode string from left to fit a given width."""
    i = 0
    j = 0
    for ch in s:
        j += __unicode_width_mapping[east_asian_width(ch)]
        if width < j:
            break
        i += 1
    return s[:i]


@types(s=String, width=int)
def unicode_right(s, width):
    """Cut unicode string from right to fit a given width."""
    i = len(s)
    j = 0
    for ch in reversed(s):
        j += __unicode_width_mapping[east_asian_width(ch)]
        if width < j:
            break
        i -= 1
    return s[i:]


@types(encoding_list=(String, ListOf(String)))
def unicode_decode(data, encoding_list):
    """
    Decode string data with one or more encodings, trying sequentially
    :param data: bytes: encoded string data
    :param encoding_list: list[string] or string: encoding names
    :return: string: decoded string
    """
    assert encoding_list, 'encodings must not be empty.'

    xs = distinct(encoding_list if isinstance(encoding_list, list) else [encoding_list])
    first_exp = None
    for i, encoding in enumerate(xs):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as e:
            if i == 0:
                first_exp = e
    raise first_exp
