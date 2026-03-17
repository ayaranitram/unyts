# unyts Quick Reference Card

**Version**: 0.10.1 | **Updated**: 2026-02-27

---

## Installation

```bash
# Install
pip install unyts

# Upgrade
pip install --upgrade unyts

# Clear old caches after upgrade
python -c "from unyts import delete_cache; delete_cache()"
```

---

## Basic Usage

### Import
```python
from unyts import units, convert, Unit
```

### Simple Conversions
```python
# Direct conversion
result = convert(100, 'm', 'ft')  # 328.084

# With units() objects
distance = units(100, 'm')
in_feet = distance.convert('ft')  # or distance.to('ft')
```

### Creating Quantities
```python
from unyts import units

# Simple quantities
length = units(10, 'm')
mass = units(50, 'kg')
time = units(5, 's')

# With arrays
import numpy as np
distances = units([10, 20, 30], 'km')
```

---

## Arithmetic Operations

```python
# Addition/Subtraction (auto-converts units)
total = units(5, 'm') + units(200, 'cm')  # 7 m

# Multiplication
area = units(10, 'm') * units(5, 'm')  # 50 m²
force = units(10, 'kg') * units(9.8, 'm/s2')  # 98 kg*m/s²

# Division
speed = units(100, 'm') / units(10, 's')  # 10 m/s
ratio = units(50, 'kg') / units(2, 'm3')  # 25 kg/m³

# Power
area = units(5, 'm') ** 2  # 25 m²
volume = units(5, 'm') ** 3  # 125 m³
```

---

## Comparisons

```python
# Auto-converts for comparison
units(1, 'km') > units(500, 'm')  # True
units(100, 'cm') == units(1, 'm')  # True

# Precision-aware equality
a = units(1.0001, 'm')
b = units(1.0002, 'm')
a.equals(b, precision=3)  # True
```

---

## Compound Units

```python
# Ratio units
density = units(1000, 'kg/m3')
pressure = units(100, 'kPa')
pressure_grad = units(0.5, 'psi/ft')

# Product units
torque = units(50, 'N*m')
energy = units(1000, 'kg*m2/s2')  # Same as Joules

# Complex units
productivity = units(100, 'bbl/day/psi')
```

---

## Unit Properties

```python
quantity = units(100, 'm/s')

# Access properties
quantity.value      # 100
quantity.unit       # 'm/s'
quantity.values     # 100 (alias)
quantity.units      # 'm/s' (alias)
quantity.dtype      # dtype (for arrays)

# Type checking
isinstance(quantity, Unit)  # True
```

---

## Conversion Methods

```python
length = units(100, 'm')

# Convert to different unit
length.convert('ft')     # Returns new Unit object in feet
length.to('km')          # Alias for convert()

# Round
length.round(2)          # Round to 2 decimal places

# Flatten arrays
arr = units([[1, 2], [3, 4]], 'm')
flat = arr.flatten()     # [1, 2, 3, 4] m
```

---

## Advanced Features (v0.10.1)

### Check Conversion Feasibility
```python
from unyts import convertible

if convertible('joule', 'BTU'):
    result = convert(1000, 'joule', 'BTU')
    print(f"Conversion successful: {result}")
else:
    print("No conversion path found")
```

### Export Network
```python
from unyts import network_to_frame

# Export to pandas DataFrame
df = network_to_frame()
print(df.head())
# Columns: source, target, lambda
```

---

## Configuration

```python
from unyts import unyts_parameters_

# Display conversion paths
from unyts import print_path
print_path(True)

# Verbosity
from unyts import verbose
verbose(2)  # 0=quiet, 1=info, 2=debug, 3=very verbose

# Search algorithm
from unyts import set_algorithm
set_algorithm('lean_BFS')  # Default, faster
set_algorithm('BFS')       # Classic BFS

# Timeout for searches
from unyts import set_timeout
set_timeout(60)  # 60 seconds

# Logging level
from unyts import set_logging_level
set_logging_level('INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Reset all tuning parameters to package defaults
from unyts import reset_default_parameters
reset_default_parameters()

# Direct parameter access
unyts_parameters_.max_generations_ = 25  # Search depth
unyts_parameters_.reduce_parentheses_ = True  # Simplify notation
unyts_parameters_.save_params()  # Save permanently
```

---

## Cache Management

```python
from unyts import save_memory, load_memory, clean_memory, delete_cache

# Save conversion paths
save_memory()

# Load cached paths
load_memory()

# Clean specific cache
clean_memory()

# Delete all caches (fresh start)
delete_cache()
```

---

## Oil & Gas Specific

```python
# Formation Volume Factor
from unyts import set_fvf, get_fvf
set_fvf(1.2)  # Set FVF
fvf = get_fvf()  # Get current FVF

# Density
from unyts import set_density, get_density
set_density(0.85)  # g/cm³
density = get_density()

# Typical O&G units
rate = units(1000, 'bbl/day')
pressure = units(3000, 'psi')
productivity = rate / pressure  # bbl/day/psi
```

---

## GUI

```bash
# Launch from command line
python -m unyts
```

```python
# Launch from Python
from unyts import start_gui
start_gui()
```

**GUI Features**:
- Real-time conversion
- Path visualization
- Cache bypass option
- Enter key support
- Input validation

---

## Common Unit Abbreviations

### Length
`m, km, cm, mm, ft, in, yd, mile, angstrom, parsec`

### Mass
`kg, g, mg, lb, oz, ton, tonne`

### Time
`s, min, hr, day, week, month, year`

### Temperature
`K, C, F, R` (Kelvin, Celsius, Fahrenheit, Rankine)

### Pressure
`Pa, kPa, MPa, psi, bar, atm, torr`

### Volume
`m3, l, ml, gal, bbl, ft3, in3`

### Energy
`J, kJ, cal, kcal, BTU, kWh, eV`

### Power
`W, kW, MW, hp`

### Data
`b, B, kb, KB, Mb, MB, Gb, GB, TB` (bit, byte)

---

## SI Prefixes

| Prefix | Symbol | Factor | Example |
|--------|--------|--------|---------|
| quetta | Q | 10³⁰ | Qm |
| ronna | R | 10²⁷ | Rg |
| yotta | Y | 10²⁴ | Ym |
| zetta | Z | 10²¹ | Zg |
| exa | E | 10¹⁸ | Em |
| peta | P | 10¹⁵ | Pm |
| tera | T | 10¹² | TB |
| giga | G | 10⁹ | GW |
| mega | M | 10⁶ | MHz |
| kilo | k/K | 10³ | km |
| milli | m | 10⁻³ | mm |
| micro | µ/u | 10⁻⁶ | µg |
| nano | n | 10⁻⁹ | nm |
| pico | p | 10⁻¹² | ps |
| femto | f | 10⁻¹⁵ | fm |
| atto | a | 10⁻¹⁸ | as |
| zepto | z | 10⁻²¹ | zm |
| yocto | y | 10⁻²⁴ | ym |
| ronto | r | 10⁻²⁷ | rm |
| quecto | q | 10⁻³⁰ | qm |

---

## Performance Tips

1. **Import once** - Import time is 0.08s, but first conversion builds database (~14s)
2. **Reuse Unit objects** - Faster than creating new ones
3. **Use cache** - Subsequent conversions are <1ms
4. **Lean BFS** - Default algorithm is optimized (80% faster)
5. **Clear old caches** - After upgrade: `delete_cache()`

---

## Error Handling

```python
from unyts.errors import (
    WrongUnitsError,
    WrongValueError,
    NoConversionFoundError,
    NoFVFError,
    SearchTimeoutError
)

try:
    result = convert(100, 'invalid_unit', 'km')
except NoConversionFoundError as e:
    print(f"Error: {e.message}")
except SearchTimeoutError as e:
    print(f"Timeout: {e.message}")
```

---

## Type Checking

```python
from unyts import Unit, is_Unit, valid_unit

# Check if object is a Unit
obj = units(100, 'm')
isinstance(obj, Unit)  # True
is_Unit(obj)  # True

# Validate unit string
valid_unit('m/s')  # True
valid_unit('xyz')  # False
```

---

## NumPy & Pandas Integration

```python
import numpy as np
import pandas as pd

# NumPy arrays
arr = units(np.array([1, 2, 3, 4, 5]), 'km')
in_miles = arr.convert('miles')

# Indexing
arr[0]  # 1 km
arr[1:3]  # [2, 3] km

# Pandas (via convert_for_SimPandas)
# Works with pandas Series and DataFrames
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Overview and quick start |
| [USAGE.md](USAGE.md) | Comprehensive guide |
| [CHANGELOG.md](CHANGELOG.md) | Complete version history |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | v0.10.1 highlights |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Upgrade from v0.9.15 |
| [VERSION_HISTORY.md](VERSION_HISTORY.md) | Module versions |
| [unyts_demo.ipynb](unyts_demo.ipynb) | Interactive tutorial |

---

## Links

- **GitHub**: https://github.com/ayaranitram/unyts
- **PyPI**: https://pypi.org/project/unyts/
- **Issues**: https://github.com/ayaranitram/unyts/issues
- **License**: MIT

---

## Quick Examples

```python
# Temperature
temp_c = units(25, 'C')
temp_f = temp_c.convert('F')  # 77 F

# Speed
speed_kmh = units(100, 'km/hr')
speed_mph = speed_kmh.convert('mph')  # 62.137 mph

# Energy
energy_j = units(1000, 'J')
energy_cal = energy_j.convert('cal')  # 239.006 cal

# Data
data_mb = units(100, 'MB')
data_gb = data_mb.convert('GB')  # 0.1 GB

# Pressure gradient
grad = units(0.465, 'psi/ft')
grad_si = grad.convert('kPa/m')  # 10.515 kPa/m
```

---

**Version 0.10.1** - The fastest unit conversion library for Python! 🚀
