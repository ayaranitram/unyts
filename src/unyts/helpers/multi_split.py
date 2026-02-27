# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 13:12:52 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>

helper functions for units modules
"""

__version__ = '0.5.3'
__release__ = 20260227
__all__ = ['multi_split']

from typing import Sequence, List, Union, Optional


def multi_split(string: str,
                sep: Union[str, Sequence[str]] = ('*', '/'),
                remove: Optional[Union[str, Sequence[str]]] = (' ',)
                ) -> List[str]:
    """
    receives a string and returns a list with string split by all the separators in sep.
    the default separator is the blank space ' '.
    use the remove parameter to indicate the separators that must not be reported in the output list.
    by default, the blank space is not reported.
    """
    if not isinstance(string, str):
        raise TypeError('string must be str')

    # normalize sep and remove to lists of strings
    if isinstance(sep, str):
        sep = [sep]
    else:
        sep = list(sep)

    if remove is None:
        remove = []
    elif isinstance(remove, str):
        remove = [remove]
    else:
        remove = list(remove)

    # eliminate duplicated separators
    sep = list(set(sep))
    # eliminate duplicated strings to remove
    remove = list(set(remove))

    # sort sep by Length
    s = len(sep)
    for i in range(s - 1):
        for j in range(s - i - 1):
            if len(sep[j]) < len(sep[j + 1]):
                sep[j], sep[j + 1] = sep[j + 1], sep[j]

    # initialize counters
    string_list = []
    i, x, t = 0, 0, len(string)
    # loop through the entire string
    while i < t:
        found = False  # flag for found separator
        # look for each separator
        for se in sep:
            s = len(se)
            if (i + s <= t) and string[i:i + s] == se:
                string_list += [string[x:i], se]
                x = i + s
                i += s
                found = True
                break
        i += 1 if not found else 0
    string_list += [string[x:]]

    # clean the output
    new_list = [part for part in string_list if part not in (remove + [''])]
    return new_list
