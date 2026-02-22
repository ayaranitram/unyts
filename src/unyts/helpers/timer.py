import time
from ..parameters import unyts_parameters_

def timeit(func):
    def wrap_func(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__!r} execution time: {end - start} seconds")
        return result
    if unyts_parameters_._timing:
        return wrap_func
    else:
        return func