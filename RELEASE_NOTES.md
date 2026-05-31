# unyts Release Notes

---

## v1.0.2 — May 31, 2026

### 🐛 Bug Fixes

#### Compound-Unit Gradient Correction (`converter.py`)

Two bugs caused incorrect results whenever an **affine** (offset-based) unit appeared as a token inside a ratio/compound unit — e.g. `psig/ft`, `g/cc`, `lb/ft³`, `SgO`:

1. **Closure-over-loop-variable in bridge selection** — conversion functions in `_ratio_conversion_including_children` captured loop variables by reference, so all bridge candidates silently used the last iteration's values. Fixed with a `_make_conversion(f, t)` factory that captures each pair by value.

2. **Affine offset leaked into compound factor** — the token conversion factor was computed as the absolute value `f(1)`, which includes the additive offset for gauge pressure (`1 psig ≈ 108 kPa` absolute). This inflated compound results by ~14.696×: `psig/ft → kPa/m` returned **355** instead of the correct **22.62**; `g/cc → MPa/km` returned **154** instead of **9.807**. Fixed by using the slope `f(1) − f(0)` instead of the raw absolute value.

### 🧪 Test Coverage
- Added Excel reference rows for pressure-gradient and density-gradient conversions: `psig/ft → kPa/m`, `psia/ft → kPa/m`, `psi/ft → kPa/m`, `psig/ft → MPa/km`, `g/cc → MPa/km`, `lb/ft³ → kPa/m`, `SgO → MPa/km`
- Documented known C++/Python gauge-naming divergence in parity test suite (`_CPP_GAUGE_DIVERGENCE_ROWS`)

---

# unyts v1.0.0 Release Notes

**Release Date**: April 7, 2026

## 🎉 Major Release Highlights

This is the most significant performance and feature update in unyts history, delivering **transformative improvements** to import speed, comprehensive testing infrastructure, enhanced error handling, and numerous quality-of-life improvements.

---

## ⚡ Performance Breakthroughs

### 200× Faster Imports
- **Import time**: 14.5s → **0.08s** (98.4% reduction)
- Uses PEP 562 lazy loading to defer heavy modules
- Zero-wait startup for CLI tools and quick scripts

### 60% Faster Database Builds
- **First build**: 40s → **16-17s**
- Optimized ProductivityIndex generation
- Pre-filtering reduces iterations by 99%
- Parallel thread execution

### 78% Faster Rebuilds
- **Cached rebuild**: 40s → **9s**
- Persistent caching with cloudpickle
- Sub-millisecond cache access
- 525 MB optimized cache storage

### Background I/O
- **19 seconds** of cache writes moved to background
- Non-blocking initialization
- Atomic file writes prevent corruption

---

## ✨ Key New Features

### 🔍 Enhanced Search Algorithm
- **Lean BFS**: 80% search space reduction
- Configurable descendant depth (default: 25 generations)
- SlimUDigraph for lightweight operations
- Intelligent pre-screening before search

### 🛡️ Alias Conflict Detection
- `collect_alias_conflicts()` - Detect ambiguous unit names
- ALIAS_PRIORITY system for automatic resolution
- Protected prefix combinations (e.g., 'rm3' always = reservoir m³)
- Documented intentional ambiguities

### 🎨 GUI Improvements
- "Repeat search" checkbox to bypass cache
- Scrolling marquee path display
- Real-time validation feedback
- Enter key support

### 🔧 New API Functions
- `convertible()` - Check if conversion possible
- `network_to_frame()` - Export network to DataFrame
- `delete_cache()` - Clear all caches
- Enhanced configuration with new parameters

### 📊 Unit Type Expansions
- **New SI prefixes**: Q (quetta), R (ronna), r (ronto), q (quecto)
- **Full SI range**: 10⁻³⁰ to 10³⁰
- Enhanced compound unit support
- Volt*Farad ↔ Coulomb shortcuts

---

## 🔬 Testing & Quality

### Comprehensive Test Suite
- 9+ test modules with extensive coverage
- New tests for alias conflicts and ambiguous units
- Session fixtures with automatic cache clearing
- CI/CD with GitHub Actions

### Enhanced Error Messages
- Contextual information with conversion paths
- Timeout details with remaining seconds
- Multiple input format support
- Better validation feedback

---

## 📚 Documentation

### New Guides
- Complete optimization summary
- Lazy loading implementation details
- Comprehension optimization guide
- Migration guide from 0.9.15

### Improved Logging
- Dual-mode support (Jupyter + Console)
- Color-coded output (ANSI/HTML)
- Configurable log levels
- Auto-detection of environment

---

## 🐛 Critical Bug Fixes

- ✅ Fixed null pointer in cache loading
- ✅ Resolved circular import issues
- ✅ Prevented cache corruption
- ✅ Protected prefix collision handling
- ✅ Enhanced edge case handling

---

## 🔄 Backward Compatibility

**100% backward compatible** - No breaking changes. All existing code will continue to work without modifications.

---

## 📦 Installation

### New Installation
```bash
pip install unyts
```

### Upgrade from Previous Version
```bash
pip install --upgrade unyts
```

### Post-Upgrade (Optional)
```python
from unyts import delete_cache
delete_cache()  # Clear old cache files for best performance
```

---

## 🚀 Quick Start

```python
from unyts import units, convert

# Create quantities with units
distance = units(100, 'm')
time = units(10, 's')

# Automatic unit arithmetic
speed = distance / time
print(speed)  # 10.0 m/s

# Direct conversion
result = convert(1, 'km', 'miles')
print(result)  # 0.621371192...

# Check if conversion possible
from unyts import convertible
if convertible('m', 'ft'):
    print("Conversion available!")

# Launch GUI
from unyts import start_gui
start_gui()
# Or from command line: python -m unyts
```

---

## 📊 Performance Comparison

| Operation | v0.9.15 | v1.0.0 | Improvement |
|-----------|---------|---------|-------------|
| **Import** | 14.5s | 0.08s | **200× faster** |
| **First Build** | 40s | 16-17s | **60% faster** |
| **Cached Rebuild** | 40s | 9s | **78% faster** |
| **Cache Access** | N/A | <1µs | **Real-time** |

---

## 🎯 Use Cases

Perfect for:
- ✅ Scientific computing with multiple unit systems
- ✅ Engineering calculations with automatic conversions
- ✅ Oil & gas industry (FVF, reservoir volumes, production rates)
- ✅ Data analysis with pandas integration
- ✅ Educational tools for unit conversion
- ✅ Quick conversions via GUI

---

## 🔗 Links

- **GitHub**: https://github.com/ayaranitram/unyts
- **PyPI**: https://pypi.org/project/unyts/
- **Issues**: https://github.com/ayaranitram/unyts/issues
- **Demo Notebook**: [unyts_demo.ipynb](unyts_demo.ipynb)

---

## 👥 Contributors

Thanks to everyone who contributed to this release through testing, bug reports, and feedback!

---

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details of all changes.

---

**This release transforms unyts into a high-performance, production-ready unit conversion library while maintaining its ease of use and comprehensive feature set.**
