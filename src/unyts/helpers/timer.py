import time
from ..parameters import unyts_parameters_

def timeit(func):
    def wrap_func(*args, **kwargs):
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