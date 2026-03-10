import pytest

from unyts.parameters import unyts_parameters_
from unyts.database import clean_memory


@pytest.fixture(autouse=True)
def manage_cache():
    """Autouse fixture executed before and after each test.

    The unit tests exercise the conversion network extensively.  By default
    the library caches every successful search path in
    ``units_network.memory``.  Running the full suite previously caused
    interned path lists (one for each pair of units) to accumulate, eating
    dozens of gigabytes of RAM.  Clearing the cache and disabling the
    feature for the duration of the tests keeps memory consumption under
    control while still exercising functionality.
    """
    # entering test: disable persistent caching and drop any previous data
    unyts_parameters_.cache_ = False
    clean_memory()
    yield
    # after test: also clear in case the test temporarily re-enabled it
    clean_memory()
