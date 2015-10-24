from __future__ import division, print_function, absolute_import, unicode_literals

import six

__all__ = ['get_single_item', 'get_single_key', 'get_single_value', 'distinct']


def get_single_item(d):
    """Get an item from a dict which contains just one item."""
    assert len(d) == 1, 'Single-item dict must have just one item, not %d.' % len(d)
    return next(six.iteritems(d))


def get_single_key(d):
    """Get a key from a dict which contains just one item."""
    assert len(d) == 1, 'Single-item dict must have just one item, not %d.' % len(d)
    return next(six.iterkeys(d))


def get_single_value(d):
    """Get a value from a dict which contains just one item."""
    assert len(d) == 1, 'Single-item dict must have just one item, not %d.' % len(d)
    return next(six.itervalues(d))


def distinct(xs):
    """Get the list of distinct values with preserving order."""
    # don't use collections.OrderedDict because we do support Python 2.6
    seen = set()
    return [x for x in xs if x not in seen and not seen.add(x)]
