from __future__ import division, print_function, absolute_import, unicode_literals

import six


class CaseClass(object):
    """
    Implementation like 'case class' in Scala language

    This class can order if all the element can order.

    Example:
        class Coord(CaseClass):
            def __init__(self, x, y):
                super(Coord, self).__init__(('x', x), ('y', y))

        a = Coord(123, 45)
        a.x  # 123
        a.y  # 45
        str(a)  # 'Coord(x=123, y=45)'
        b = a.copy(y=54)
        str(b)  # 'Coord(x=123, y=54)'
        a < b  # True
    """

    def __init__(self, *args, **kwargs):
        """
        :param args: list of tuple of field key and value
        :param kwargs: specify field key with value
                       Note that keys do NOT keep order. The order is rearranged in lexicographical.
        """
        keys = []
        for k, v in list(args) + sorted(kwargs.items()):
            if not isinstance(k, six.string_types):
                raise TypeError('Field key must be a string: %s' % k)
            if k in keys:
                raise ValueError('Found duplicate key name: %s' % k)
            keys.append(k)
            setattr(self, k, v)
        self._keys = keys

    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('unorderable types: %s() < %s()' % (self.__class__.__name__, other.__class__.__name__))

        for k in self._keys:
            a, b = getattr(self, k), getattr(other, k)
            if a is not None or b is not None:
                if a < b:
                    return -1
                if a > b:
                    return 1
        return 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        for k in self._keys:
            a, b = getattr(self, k), getattr(other, k)
            if a is not None or b is not None:
                if a != b:
                    return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%r' % (k, getattr(self, k)) for k in self._keys))

    def copy(self, **kwargs):
        """
        :param kwargs:
        :return: copy of this object modifying the kwargs
        """
        for k in kwargs:
            assert k in self._keys, 'Invalid key: %s' % k

        d = self.values()
        d.update(kwargs)
        return self.__class__(**d)

    def values(self):
        """
        :return: key-value dict : { string: any }
        """
        return dict((k, getattr(self, k)) for k in self._keys)
