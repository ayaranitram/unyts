# Using the `unyts` Package

This document provides a quick start guide and reference for working with **unyts**.  It's intended for end users who just want to make conversions or perform unit-aware calculations.

---

## Installation

Install from PyPI with `pip`:

```bash
to install:    pip install unyts
```

To upgrade to the latest release:

```bash
pip install --upgrade unyts
```

The core functionality is pure Python and has no hard dependencies, but the package can make use of the following optional libraries if they are available:

* **NumPy** – handles iterable values such as arrays and lists.
* **Pandas** – recognizes `Series`/`DataFrame` objects.
* **cloudpickle** – enables caching of the network and search memory for fast startup.
* **openpyxl** – required only when exporting the network to an Excel-like DataFrame.

If you plan to persist caches, install `cloudpickle` to avoid warnings.

---

## Quick start

Import the top-level helpers and try a conversion right away:

```python
from unyts import convert, units

# simple numeric conversion
print(convert(10, 'ft', 'm'))  # -> 3.048

# create `Unit` objects via the `units()` helper
q = units(6, 'in') + units(1, 'ft')
print(q)                        # -> 18_in
```

You can also work directly with the `Unit` type for `isinstance` checks:

```python
from unyts import Unit

print(isinstance(q, Unit))      # True
```

A more extensive interactive walkthrough is available in the `unyts_demo.ipynb` notebook shipped with the repository.

---

## Core API

### `convert(value, from_units, to_units)`

A functional converter.  `value` may be a scalar, list, NumPy array, etc.  Unit strings can be simple (e.g. `'m'`) or compound (e.g. `'kg/m3'`).

```python
convert(1, 'km', 'm')          # 1000.0
convert([1,2,3], 'ft', 'cm')   # [30.48, 60.96, 91.44]
```

### `units(value, units)`

Factory for `Unit` instances.  Performs the right subclass lookup and attaches the quantity to the value.

```python
length = units(5, 'm')
area   = units(20, 'ft2')
```

Arithmetic and comparison operators between `Unit` objects automatically convert as needed.

### `Unit`

The base class for all unit‑aware values.  You normally do not instantiate it directly; use `units()` instead.  However, the class is exposed for type checks:

```python
isinstance(length, Unit)  # True
```

Additional helpers and utilities such as `set_fvf`, `get_fvf`, `load_memory`, `save_memory`, etc. are available at the package level or via the `database` module (see the module docstrings).

### `convertible(from_units, to_units)`

Test whether a conversion path exists **without** actually performing the conversion.  Returns `True` or `False`.

```python
from unyts import convertible

convertible('ft', 'm')    # True
convertible('ft', 'kg')   # False
```

### `valid_unit(string)`

Check whether a string is recognized as a valid unit name:

```python
from unyts import valid_unit

valid_unit('ft')     # True
valid_unit('xyz')    # False
```

### `is_Unit(obj)`

Check whether an object is a `Unit` instance:

```python
from unyts import is_Unit, units

is_Unit(units(1, 'm'))   # True
is_Unit(42)               # False
```

### `network_to_frame()`

Export the entire conversion network to a Pandas `DataFrame` for inspection or analysis:

```python
from unyts import network_to_frame

df = network_to_frame()
print(df.head())
# Columns include: source, target, lambda
```

Requires `openpyxl` or `pandas` to be installed.

### Configuration functions

| Function | Purpose |
|----------|---------|
| `set_algorithm(name)` | Switch search strategy: `'BFS'`, `'lean_BFS'` (default), `'hybrid_BFS'` |
| `set_timeout(seconds)` | Maximum time allowed per search (default 30 s) |
| `set_parallel(flag)` | Enable or disable parallel search threads |
| `set_fvf(value)` | Set the formation volume factor for reservoir conversions |
| `set_density(value)` | Set the default density for mass ↔ volume conversions |
| `get_density()` / `get_fvf()` | Retrieve current density / FVF values |
| `set_logging_level(level)` | Adjust log verbosity: `'DEBUG'`, `'INFO'`, `'WARNING'`, `'ERROR'` |
| `reset_default_parameters()` | Restore all tuning/configuration parameters to package defaults |

### Unit operators

`Unit` objects support a range of arithmetic and comparison operators.  Some noteworthy additions:

```python
from unyts import units

# ratio via matmul (@)
units(12, 'in') @ units(1, 'ft')   # ratio in in/ft

# floor division and modulo
units(7, 'm') // units(2, 'm')     # 3
units(7, 'm') % units(2, 'm')      # 1 m

# rounding
round(units(3.14159, 'm'), 2)      # 3.14 m
```

---

## GUI

A simple tkinter-based GUI is bundled with the package.  Launch it from the command line:

```bash
python -m unyts
```

Type a value and the source/target units, then click **Convert** or press Enter.  The GUI is useful for quick manual look‑ups.

---

## Caching and performance

Building the units network can be time‑consuming on first import.  `unyts` caches both the network and the conversion search memory in the user folder (controlled by the `unyts_parameters_` object).

*To explicitly clear caches:*

```python
from unyts import delete_cache

delete_cache()
```

Search memory is automatically saved when the package shuts down and reloaded on startup.  You can also call `save_memory()` and `load_memory()` manually.

If you modify the underlying dictionaries or wish to rebuild the network from scratch, deleting the cache is recommended.  The network builder is now robust to duplicate unit names and will log debug messages if a node is skipped.

---

## Advanced usage

### Unit networks and conversions

The package builds a directed graph (`UDigraph`) of unit nodes, allowing conversions between any two units connected by a path.  You rarely need to interact with this directly, but the network can be exported for inspection using the helpers in `database`.

### Extending with custom units

You can define your own units via the `UserUnits` class (see `src/unyts/units/custom.py`).  Custom units are added to the network automatically when the package loads.

### Python 3.14 parallel support

If running on Python 3.14 or later with the GIL-free build, certain internal loops (network creation and dictionary loading) use true parallelism to speed startup.  This is transparent to users.

---

## Troubleshooting & FAQs

* **`WrongUnitsError` when converting** – check that the unit string is valid and spelled correctly.
* **`Duplicate node` exceptions** – the graph builder no longer raises on duplicates; if you see this error please upgrade.
* **Cache corruption** – if a cache file fails to load, the package will log a warning and start with an empty memory. Delete the cache file manually to recover.

---

For more examples see the demo notebook or the tests in `tests/`.  If you have questions or run into issues, open an issue on the GitHub repository.

Happy converting! 🚀
