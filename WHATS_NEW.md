# What's New in unyts — from v0.9.15 to v0.10.5

This document summarizes everything that has changed since the last stable release v0.9.15 (commit 9525a4f).  It is written from a **user perspective** — what you can do now that you couldn't before, what got faster, and what was fixed.

---

## At a Glance

| Area | Improvement |
|------|-------------|
| **Import speed** | 200× faster (14.5 s → 0.08 s) |
| **First build** | 60% faster (40 s → 16–17 s) |
| **Cached rebuild** | 78% faster (40 s → 9 s) |
| **New API functions** | 12 new public functions |
| **Search algorithm** | 80% smaller search space with Lean BFS |
| **Unit operators** | `@`, `//`, `%`, `round()` on Unit objects |
| **GUI** | Enter key, repeat‑search, scrolling path display |
| **SI prefixes** | Complete 10⁻³⁰ – 10³⁰ range (quecto to quetta) |
| **Backward compatible** | 100% — no code changes required to upgrade |

---

## 1  Performance

### Instant imports

The package now uses **PEP 562 lazy loading**: heavy modules such as the database, converter and GUI are loaded only when first accessed.  A bare `from unyts import convert` no longer triggers the full network build.

### Faster network building

| Scenario | v0.9.15 | v0.10.5 |
|----------|---------|---------|
| `import unyts` | 14.5 s | 0.08 s |
| First conversion (triggers build) | ~40 s | 16–17 s |
| Subsequent import (cached) | ~40 s | ~9 s |
| Cached search lookup | — | < 1 µs |

### Persistent caching

Six specialized cache files (`units_network`, `units_dictionary`, `search_memory`, `temperature_ratio_conversions`, `unitless_names`, `all_units`) are written in the background using asynchronous I/O and atomic writes.  Caches survive process restarts and are loaded transparently on import.

To clear all caches at once:

```python
from unyts import delete_cache
delete_cache()
```

---

## 2  New Functions

### `convertible(from_unit, to_unit)`

Check whether a conversion path exists **before** attempting conversion.  Returns `True`/`False` without actually computing the result.

```python
from unyts import convertible

convertible('ft', 'm')       # True
convertible('ft', 'kg')      # False
```

### `network_to_frame()`

Export the entire conversion network to a Pandas DataFrame for inspection or analysis.

```python
from unyts import network_to_frame

df = network_to_frame()
print(df.head())
# Columns: source, target, lambda
```

### `delete_cache()`

Remove every cache file in a single call.  Useful when upgrading or when the network needs to be rebuilt from scratch.

### `start_gui()`

Launch the GUI programmatically:

```python
from unyts import start_gui
start_gui()
```

Or from the command line:

```bash
python -m unyts
```

### Configuration helpers

| Function | Purpose |
|----------|---------|
| `set_algorithm(name)` | Switch search strategy: `'BFS'`, `'lean_BFS'` (default), `'hybrid_BFS'` |
| `get_algorithm()` | Return the current search algorithm |
| `set_timeout(seconds)` | Maximum time allowed per search (default: 30 s) |
| `get_timeout()` | Return the current timeout |
| `set_parallel(flag)` | Enable / disable parallel search threads |
| `get_parallel()` | Return the current parallel setting |
| `set_logging_level(level)` | Adjust log verbosity at runtime (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `set_fvf(value)` | Set the formation‑volume‑factor for reservoir conversions |
| `set_density(value)` | Set the default density for mass ↔ volume conversions |
| `is_Unit(obj)` | Check whether an object is a Unit instance |
| `valid_unit(string)` | Validate a unit string against the loaded dictionary |

---

## 3  Enhanced Unit Class

### New properties

| Property | Description |
|----------|-------------|
| `.dtype` | NumPy datatype (when the value is an array) |
| `.name` | Custom metadata string attached to the object |
| `.values` | Alias for `.value` (Pandas‑style consistency) |
| `.units` | Alias for `.unit` |

### New operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `@` | Unit ratio (matmul) | `units(6, 'ft') @ units(12, 'in')` → ratio in ft/in |
| `//` | Floor division | `units(7, 'm') // units(2, 'm')` |
| `%` | Modulo | `units(7, 'm') % units(2, 'm')` |
| `round()` | Rounding | `round(units(3.14159, 'm'), 2)` → 3.14 m |

### Better value handling

- Lists and tuples passed as `value` are automatically converted to NumPy arrays.
- `flatten()` and `item()` work on array‑valued units.

---

## 4  Search Improvements

### Lean BFS (default algorithm)

A new **Lean BFS** algorithm pre‑screens the descendants of both source and target nodes before launching the breadth‑first search.  Only the relevant portion of the network is explored, reducing the search space by roughly **80%**.

### Configurable timeout

Long‑running searches are now bounded by a configurable timeout (default 30 s).  If no path is found within the limit, the search returns gracefully instead of hanging.

```python
from unyts import set_timeout
set_timeout(60)   # allow up to 60 seconds per search
```

### Hybrid search

The `hybrid_BFS` strategy runs BFS and Lean BFS in parallel (or serial, depending on `set_parallel()`) and returns the first result found.

---

## 5  New Units and Prefixes

### Complete SI prefix spectrum

Four new SI prefixes complete the range from 10⁻³⁰ to 10³⁰:

| Prefix | Symbol | Factor |
|--------|--------|--------|
| quetta | Q | 10³⁰ |
| ronna | R | 10²⁷ |
| ronto | r | 10⁻²⁷ |
| quecto | q | 10⁻³⁰ |

These are automatically applied to every base unit that accepts SI prefixes.

### Data units

Bit and byte units with both **SI** (KB, MB, GB, …) and **binary** (KiB, MiB, GiB, …) prefixes are now part of the network.

```python
from unyts import convert
convert(1, 'GB', 'MB')      # 1000.0
convert(1, 'GiB', 'MiB')    # 1024.0
```

### Expanded compound units

Product (`kg*m`), ratio (`m/s`, `psi/ft`), and power (`m²`, `ft³`) units are fully supported with automatic prefix propagation.

---

## 6  GUI Improvements

| Feature | Description |
|---------|-------------|
| **Enter key** | Press Enter to convert instantly — no need to click the button |
| **Repeat search** | Checkbox to bypass the cache and force a fresh search (useful for debugging) |
| **Scrolling path** | The full conversion path is displayed in a scrolling marquee |
| **Real‑time validation** | Visual feedback while typing unit strings |
| **Dynamic button text** | The "Convert" label appears on hover |
| **Clearer errors** | Context‑aware error messages in the GUI |

Launch from the command line with `python -m unyts` or from Python with `start_gui()`.

---

## 7  Better Error Messages

- **Contextual information**: errors now include the conversion path being attempted and the units involved.
- **Timeout details**: `SearchTimeoutError` reports the elapsed time and the configured limit.
- **Alias conflict warnings**: when a unit abbreviation maps to more than one canonical name (e.g. `'oz'` for ounce vs fluid ounce), a warning is issued with the candidates.

### Alias conflict detection

A new subsystem detects ambiguous aliases at dictionary‑load time.  Known ambiguities (such as `'w'` for week vs watt, or `'yd'` for yard vs yottadyne) are handled through a priority table.

---

## 8  Oil & Gas Features

- **Formation Volume Factor (FVF)**: `set_fvf(value)` / `get_fvf()` control the reservoir‑to‑surface volume ratio.
- **Configurable density**: `set_density(value)` / `get_density()` set the default density for mass ↔ volume conversions.
- **OGF prefixes**: MSCF, MMSCF, BSCF and similar oil‑and‑gas‑field multipliers are supported.
- **Temperature‑corrected conversions**: special handling for conversions involving temperature *differences* (e.g. °F/ft ↔ °C/m).

---

## 9  Configuration

### JSON configuration file

Settings are stored in a human‑readable `parameters.ini` (JSON format) inside the user folder (`~/.unyts/` or equivalent).  Key parameters:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `algorithm` | `"lean_BFS"` | Search strategy |
| `timeout` | `30` | Search timeout in seconds |
| `parallel` | `true` | Enable parallel search threads |
| `cache` | `true` | Persist caches to disk |
| `verbose` | `true` | Log informational messages |
| `verbose_details` | `0` | Detail level 0–3 |
| `reduce_parentheses` | `true` | Simplify unit notation |
| `max_recursion` | `5` | Maximum converter recursion depth |
| `max_generations` | `10` | Lean BFS descendant depth limit |
| `density` | `0.997` | Default density (g/cm³) for mass ↔ volume |
| `fvf` | `1.5` | Default formation volume factor |

### `unitary` module

A convenience module providing pre‑built Unit objects for common quantities:

```python
from unyts.unitary import meter, foot, kilogram, celsius, watt, hertz
print(meter.convert('ft'))   # 3.28084 ft
```

---

## 10  Bug Fixes

These are the most significant bugs fixed since v0.9.15:

| Issue | Impact | Status |
|-------|--------|--------|
| **MemoryError** during network building | ~500 MB intermediate list crashed 32‑bit Python and constrained systems | Fixed — generator expression |
| **Missing `logger.exception()`** method | Error diagnostics silently swallowed tracebacks | Fixed — method added |
| **BFS algorithm broken** by incomplete refactor | Searches found no paths, returning Empty | Fixed — set‑based BFS restored |
| **`hybrid_BFS` wrong variable** | Referenced undefined `units_network` instead of `graph` | Fixed |
| **`dataBIT`/`dataBYTE` not merged** into Data class | `NameError` when importing `unitary` module | Fixed — keys merged and removed |
| **Empty string in Dimensionless dictionary** | `units(1, '')` created invalid zero‑unit objects | Fixed — empty entry removed |
| **Over‑canonicalization** of unit strings | `'ft'` silently became `'foot'` in user‑visible output | Fixed — canonicalization removed from input path |
| **`Unit.equals()` missing `return`** | Equality comparisons always returned `None` | Fixed |
| **Density conversion tuple unpacking** | `_density_conversion` returned wrong type | Fixed |
| **Timer not reset between tests** | Timeout‑based failures when running the full test suite | Fixed — `reset_start_time()` in conftest |

---

## 11  Compatibility

**unyts v0.10.5 is 100% backward compatible with v0.9.15.**  No code changes are required to upgrade.

```bash
pip install --upgrade unyts
```

Optional: clear old caches for optimal performance with the new caching system:

```python
from unyts import delete_cache
delete_cache()
```

Supported Python versions: **3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14**.
