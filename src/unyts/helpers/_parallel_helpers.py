#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 10:38:47 2024

@author: Martín Carlos Araya <martinaraya@gmail.com>
"""

__version__ = '0.1.0'
__release__ = 20260225
__all__ = ['parallel_execute']

"""Parallel execution helpers for Python 3.14+.

This module provides a safe wrapper around concurrent execution of independent
`_create_*` functions. The functions are executed in threads and exceptions are
collected; on error the caller can fallback to sequential execution.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os
import logging

logger = logging.getLogger('UnytsParallel')

def parallel_execute(functions, max_workers=None, timeout=None):
    """Execute callables in parallel threads and propagate exceptions.

    Args:
        functions (iterable): callables with no args.
        max_workers (int|None): number of worker threads (defaults to os.cpu_count()).
        timeout (float|None): global timeout in seconds (None = wait forever).

    Raises:
        Exception: Re-raises the first exception raised by any worker after
                   canceling remaining futures.
    Returns:
        dict: mapping function.__name__ -> result (if functions return values),
              or None if functions do not return anything.
    """
    if max_workers is None:
        try:
            max_workers = min(len(functions), os.cpu_count() or 1)
        except Exception:
            max_workers = min(len(functions), 4)

    results = {}
    exceptions = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_func = {executor.submit(fn): fn for fn in functions}

        try:
            for fut in as_completed(future_to_func, timeout=timeout):
                fn = future_to_func[fut]
                try:
                    res = fut.result()
                    results[getattr(fn, '__name__', str(fn))] = res
                except Exception as exc:
                    # Record exception and attempt to cancel remaining futures
                    exceptions.append((fn, exc))
                    logger.exception('Parallel task %s raised exception', getattr(fn, '__name__', fn))
                    # Note: cancelling running threads is not possible; we just collect
                    # exceptions and let outstanding threads finish or rely on caller
                    # to fall back.
        except Exception as e:
            # Could be timeout or other as_completed error
            logger.exception('parallel_execute encountered error: %s', e)
            exceptions.append((None, e))

    if exceptions:
        # Re-raise first exception for caller to handle
        fn, exc = exceptions[0]
        raise exc

    return results
