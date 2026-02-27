# -*- coding: utf-8 -*-
"""
@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.1.0'
__release__ = 20260222

import time
from ..parameters import unyts_parameters_

def timeit(func):
    """A decorator to measure the execution time of a function and print it in a human-readable format."""
    def wrap_func(*args, **kwargs):
        """Wrap the original function to measure and print its execution time."""
        msg0 = f"{func.__name__!r} starting on: {time.ctime()}"
        print(msg0, end='\r')
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        msg1 = f"{func.__name__!r} execution time: {end - start} seconds"
        if len(msg1) < len(msg0):
            msg1 = f"{msg1}{' ' * (len(msg0) - len(msg1))}"  # Clear leftover chars
        print(msg1)
        return result
    if unyts_parameters_._timing:
        return wrap_func
    else:
        return func