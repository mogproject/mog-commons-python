from __future__ import division, print_function, absolute_import, unicode_literals


#
# functions for handling optional values
#
def omap(function, optional):
    """Map optional value"""
    return None if optional is None else function(optional)


def oget(optional, default=None):
    """Get optional value or default value"""
    return default if optional is None else optional


def ozip(*optionals):
    """Zip optional values. Return None if one value or the other is None."""
    return None if any(x is None for x in optionals) else tuple(optionals)
