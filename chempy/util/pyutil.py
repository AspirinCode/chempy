# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

from collections import namedtuple, Mapping
from functools import wraps
import warnings

from .. import __url__


def defaultnamedtuple(typename, field_names, defaults=()):
    """ Generates a new subclass of tuple with default values.

    Parameters
    ----------
    typename: string
         the name of the class
    field_names: str or iterable
        an iterable of splitable string
    defaults: iterable
        default values for field_names, counting [-len(defaults):]

    Examples
    --------
    >>> Body = defaultnamedtuple('Body', 'x y z density', (1.0,))
    >>> Body.__doc__
    'Body(x, y, z, density)'
    >>> b = Body(10, z=3, y=5)
    >>> b._asdict()
    OrderedDict([('x', 10), ('y', 5), ('z', 3), ('density', 1.0)])

    Returns
    -------
    A new tuple subclass named ``typename``
    """
    Tuple = namedtuple(typename, field_names)
    Tuple.__new__.__defaults__ = (None,) * len(Tuple._fields)
    if isinstance(defaults, Mapping):
        Tuple.__new__.__defaults__ = tuple(Tuple(**defaults))
    else:
        nmissing = len(Tuple._fields) - len(defaults)
        defaults = (None,)*nmissing + tuple(defaults)
        Tuple.__new__.__defaults__ = tuple(Tuple(*defaults))
    return Tuple


class deprecated(DeprecationWarning):
    """ search the code base for examples

    DeprecationWarning is ignored by default. Run python with -W flag or set
    the appropriate environment variable:

    ::

       $ python -c 'import warnings as w; w.warn("no", DeprecationWarning)'
       $ python -Wd -c 'import warnings as w; w.warn("no", DeprecationWarning)'
       -c:1: DeprecationWarning: no
       $ export PYTHONWARNINGS=d
       $ python -c 'import warnings as w; w.warn("no", DeprecationWarning)'
       -c:1: DeprecationWarning: no

    """

    def __init__(self, deprecated_since_version=None, will_be_missing_in=None,
                 use_instead=None, issue=None):
        self.deprecated_since_version = deprecated_since_version
        self.will_be_missing_in = will_be_missing_in
        self.use_instead = use_instead
        self.issue = issue
        self.warning_message = self._warning_message_template()

    def _warning_message_template(self):
        msg = '%(func_name)s is deprecated'
        if self.deprecated_since_version is not None:
            msg += ' since % s' % self.deprecated_since_version
        if self.will_be_missing_in is not None:
            msg += ', it will be missing in %s' % self.will_be_missing_in
        if self.issue is not None:
            assert self.issue.startswith('gh-')  # currently tracked at github
            msg += ' (see %s)' % (__url__ + '/issues/' + self.issue[3:])
        if self.use_instead is not None:
            msg += '. Use %s instead' % self.use_instead.__name__
        return msg + '.'

    def __call__(self, wrapped):
        msg = self.warning_message % {'func_name': wrapped.__name__}
        if hasattr(wrapped, '__mro__'):  # wrapped is a class
            class wrapper(wrapped):
                def __init__(self, *args, **kwargs):
                    warnings.warn(msg, DeprecationWarning, stacklevel=3)
                    wrapped.__init__(self, *args, **kwargs)

        else:  # wrapped is a function
            @wraps(wrapped)
            def wrapper(*args, **kwargs):
                warnings.warn(msg, DeprecationWarning, stacklevel=3)
                return wrapped(*args, **kwargs)

        wrapper._deprecation = self
        return wrapper
