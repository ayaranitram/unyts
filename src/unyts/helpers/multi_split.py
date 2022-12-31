# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 13:12:52 2022

@author: Martín Carlos Araya <martinaraya@gmail.com>

helper functions for units modules
"""

__version__ = '0.4.7'
__release__ = 20221229
__all__ = ['multi_split']


def multi_split(string: str,
                sep: str or tuple or list = ('*', '/'),
                remove: str or tuple or list = (' ',)
                ) -> tuple[str]:
    """
    receives a string and returns a list with string split by all the separators in sep.
    the default separator is the blank space ' '.
    use the remove parameter to indicate the separators that must not be reported in the output list.
    by default, the blank space is not reported.
    """
    assert type(string) is str

    # check sep and remove are str
    if type(sep) is str:
        sep = [sep]
    if remove is None:
        remove = []
    elif type(remove) is str:
        remove = [remove]

    # eliminate duplicated separators
    sep = list(set(sep))
    # eliminate duplicated strings to remove
    remove = list(set(remove))

    # sort sep by length
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
    return tuple(new_list)
