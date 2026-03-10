# Changelog

All notable changes to the unyts project are documented in this file.

## [0.10.1] - 2026-02-27

### 🚀 Major Performance Optimizations

#### Lazy Module Loading (200× Import Speed Improvement)
- **Import time reduced from 14.5s to 0.08s** (98.4% faster, ~200× improvement)
- Implemented PEP 562 module-level `__getattr__` mechanism for deferred imports
- Heavy modules (database.py, converter.py, unit_class.py, unitary.py, gui.py) now load only when first accessed
- Zero-wait import for CLI tools and quick scripts
- First function call includes database build (~14.5s), but subsequent operations use cached data

#### Asynchronous Cache Persistence
- **19 seconds of I/O operations moved to background thread**
- Non-blocking cache writes using atomic temp → replace pattern
- Prevents cache corruption during write operations
- Background thread `_save_cache_async()` for seamless user experience

#### Optimized Database Building
- **_complete_products pre-filtering**: 64% faster (9.63s → 3.45s, saving 6.2 seconds)
  - Pre-filter to only process entries containing '*' character
  - Reduced iterations from 19.5M entries to ~100K relevant ones
- **Improved ProductivityIndex generation**: 25% faster (8.57s → 6.43s, saving 2.1 seconds)
  - Optimized list comprehension + set.update() pattern
  - Benchmarked 7 different approaches, implemented fastest
- **Overlapped thread execution**: 20% faster database builds (-1.5 seconds)
  - ProductivityIndex and CompleteProducts run in parallel
  - Sequential 10s reduced to overlapped 6.5s

#### Persistent Caching System
- **_all_units cache**: 7 seconds saved per rebuild (89% faster in development)
  - 525 MB cache file for 23.5M-element set
  - Load time: <1 millisecond from disk vs 7.1s computation
- **Multiple specialized caches**:
  - search_memory.cache
  - units_network.cache
  - units_dictionary.cache
  - temperature_ratio_conversions.cache
  - unitless_names.cache
  - all_units.cache (NEW)

#### Performance Summary
- **Import**: 14.5s → 0.08s (**200× faster**)
- **First Database Build**: 40s → 16-17s (**60% faster**)
- **Cached Rebuild**: 40s → 9s (**78% faster**)
- **Cache Access Latency**: <1 microsecond (real-time)

### ✨ Core Functionality Enhancements

#### Enhanced Unit Class System (v0.6.7)
- **New Properties**:
  - `dtype` - NumPy datatype support for arrays
  - `name` - Custom naming for unit instances
  - `values` and `units` - Aliases for consistency with pandas-like API
- **Improved Methods**:
  - `check_value()` - Automatic list-to-array conversion
  - `check_unit()` - Enhanced unit validation
  - `flatten()` - Array flattening support
  - `item()` - Scalar extraction from arrays
  - `round(precision)` - Rounding to specified decimal places

#### Advanced Arithmetic Operations (v0.5.4)
- **New Operators**:
  - `__matmul__` (@) - Custom operator for unit ratios
  - `__round__` - Direct rounding support
  - `__floordiv__` / `__rfloordiv__` - Floor division with units
  - `__mod__` - Modulo operation support
- **Enhanced Operations**: Better handling of unit products and ratios in multiplication/division

#### Improved Conversion System (v0.8.10)
- **New Special Cases**:
  - V*F ↔ Coulomb shortcut (Volt*Farad equivalence)
  - Temperature ratio conversions with custom factors
  - Date-to-date identity checks (no conversion needed)
  - Dimensionless ↔ Percentage automatic conversion
- **Enhanced Functions**:
  - `convertible()` - Check if conversion path exists between units
  - `_get_pair_child()` - Find ratio/product children in network
  - `_get_descendants()` - Cached descendant retrieval with configurable depth

#### Lean BFS Search Algorithm (v0.6.7)
- **~80% search space reduction** through intelligent pre-screening
- Pre-screens descendants before executing BFS
- Configurable generation limit (default: 25)
- New `SlimUDigraph` class for lightweight search operations
- Significant performance improvement for complex conversion paths

### 🛡️ Error Handling & Validation

#### Enhanced Error Messages (v0.4.9)
- **Contextual information**: Errors now include conversion paths and attempted routes
- **Timeout details**: `SearchTimeoutError` shows remaining seconds and timeout limit
- **Multiple input formats**: Flexible error message construction
- All exceptions include descriptive "ERROR:" prefix and `.message` attribute

#### Alias Conflict Detection System (v0.6.0)
- **New function**: `collect_alias_conflicts()` - Detects ambiguous unit names across dictionaries
- **ALIAS_PRIORITY dictionary**: Programmatic conflict resolution (e.g., 'rm3' reserved for reservoir cubic meter)
- **Protected combinations**: Prevents prefix collisions (e.g., 'r' + 'm3' correctly handled)
- **Known ambiguities**: Documented intentional conflicts ('w' for week/watt, 'yd' for yard/yottadyne, 'pc' for parsec/picocoulomb)
- **Helper function**: `_remove_alias_from_dict()` for selective alias removal

#### Improved Validation
- Enhanced `valid_unit()` function with better string parsing
- Better type checking and automatic conversion for values
- `NoFVFError` with detailed formation volume factor messages
- Comprehensive input sanitization and validation

### 🎨 GUI Improvements (v0.4.8)

#### Enhanced Tkinter Interface
- **New features**:
  - "Repeat search" checkbox to bypass cache for testing
  - Dynamic button text ("convert" appears on hover)
  - Scrolling marquee path display showing conversion route
  - Enter key support for instant conversion
- **Improved validation**: Real-time unit and value validation with visual feedback
- **Better UX**: Gray-colored results for better readability, clearer error messages
- **Command-line launch**: `python -m unyts` starts GUI

### 📊 Data & Network Management

#### Network Export Functionality (v0.8.1)
- **New function**: `network_to_frame()` - Export unit conversion network to pandas DataFrame
- **Columns**: source, target, lambda (conversion factor)
- **Auto-deduplication**: Removes duplicate conversion paths
- Enables data analysis and visualization of the conversion network

#### Enhanced Cache Management
- **New functions**:
  - `clean_memory()` - Remove specific cache files
  - `delete_cache()` - Clear all caches at once
- **Atomic writes**: Prevents cache corruption during system crashes
- **Temperature ratio cache**: Dedicated cache for temperature difference conversions

### 🔬 Testing & Quality Assurance

#### Expanded Test Coverage
- **New test modules**:
  - `test_ambiguous_aliases.py` - Alias conflict detection and resolution
  - `test_uncertain_units.py` - Ambiguous input handling (e.g., 'oz' for ounce vs fluid ounce)
- **Enhanced existing tests**:
  - `test_converter.py` - Added SimPandas DataFrame integration tests
  - `test_helpers.py` - Comprehensive helper function coverage
  - `test_unit_class.py` - Complete API testing with edge cases
- **Session fixture improvements**:
  - Automatic cache clearing between test runs
  - Pre-import optimization for faster test execution
  - Parallel execution isolation to prevent test interference

#### CI/CD Integration
- GitHub Actions automated testing workflow
- Status badge in README showing build status
- Automated testing on push and pull requests

### 📚 Documentation & Usability

#### Comprehensive Documentation
- **New documents**:
  - `OPTIMIZATION_RESULTS.md` - Lazy loading implementation details
  - `COMPLETE_OPTIMIZATION_SUMMARY.md` - Multi-phase optimization guide
  - `lazy_loading_optimization_summary.md` - Module proxy pattern explanation
  - `comprehension_optimization_guide.md` - List comprehension improvements
- **Enhanced README**: Performance metrics, updated installation guide, feature highlights
- **Demo notebook**: Updated `unyts_demo.ipynb` with new features and examples

#### Logging System (v0.1.1)
- **Dual-mode support**: Works in both Jupyter notebooks and console
- **Color coding**: ANSI codes for terminal, HTML for notebooks
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Auto-detection**: Automatically detects Jupyter notebook environment
- **Configurable**: Runtime log level adjustment via `set_logging_level()`

#### Timer Decorator (v0.1.0)
- **@timeit decorator**: Function execution timing for performance profiling
- **Human-readable format**: Auto-formats to µs, ms, or s
- Used throughout codebase for optimization benchmarking

### ⚙️ Configuration & Parameters (v0.6.13)

#### New Configuration Parameters
- `max_generations_` - Maximum descendant generation limit for search screening (default: 25)
- `show_version_` - Toggle version display on import (default: True)
- `reduce_parentheses_` - Simplify unit notation by reducing redundant parentheses (default: True)
- `verbose_details_` - Logging detail level from 0-3 (default: 0)

#### Improved Configuration Management
- `get_user_folder()` - Platform-specific config directory (~/.unyts/)
- `reset_start_time()` / `is_intime()` - Timeout management for long searches
- `set_logging_level()` - Runtime log level adjustment
- **Backup system**: `parameters.backup` for version migration and recovery
- **JSON-based**: Human-readable `parameters.ini` configuration file

### 🔄 Infrastructure & Build

#### Updated Dependencies
- **Core dependencies**:
  - `stringthings` - String manipulation utilities
  - `cloudpickle` - Efficient serialization for caching
- **Optional dependencies**: NumPy, Pandas, openpyxl (for advanced features)
- **Python support**: 3.7, 3.8, 3.9, 3.10, 3.11
- **License**: MIT

#### Package Structure Improvements
- Modular organization with clear separation of concerns
- Lazy loading infrastructure throughout codebase
- Clean entry point: `python -m unyts` for GUI
- Improved `__main__.py` for command-line invocation

### 🐛 Bug Fixes

#### Critical Fixes
- **Null pointer in memory load**: Check file existence before loading cache, prevents crashes on first run
- **Circular import resolution**: Completely resolved circular import chain in lazy loading system
- **Cache corruption prevention**: Atomic file writes with temp → replace pattern
- **Prefix collision protection**: Protected combinations prevent unwanted units (e.g., 'rm3' always means "reservoir cubic meter")

#### Minor Fixes
- Fixed edge cases in unit string parsing
- Improved error messages for invalid conversions
- Better handling of empty or null values
- Resolved ambiguous alias warnings

### 📝 Helper Utilities

#### Enhanced String Tools (v0.5.2)
- `split_ratio()` - Parse ratio units (e.g., "m/s" → ["m", "s"])
- `split_product()` - Parse product units (e.g., "kg*m" → ["kg", "m"])
- `reduce_parentheses()` - Simplify unit notation
- `reduce_units()` - Normalize unit strings

#### Type Conversion Utilities (v0.4.10)
- `caster()` - Convert strings to appropriate numeric types (int, float, complex)
- `to_number()` - Alias for caster()
- `is_number()` - Validate numeric string formats

#### Multi-Split Function (v0.5.3)
- Split strings on multiple delimiters simultaneously
- Used for parsing complex unit expressions
- More efficient than chaining multiple split operations

### 🔮 Unit Type Expansions

#### New SI Prefixes (v0.1.1)
- **Added**: Q (quetta, 10³⁰), R (ronna, 10²⁷), r (ronto, 10⁻²⁷), q (quecto, 10⁻³⁰)
- **Complete range**: Now supports 10⁻³⁰ to 10³⁰ (full SI prefix spectrum)
- Complies with latest SI standards

#### Enhanced Unit Definitions
- **Geometry** (v0.5.31): Length, Area, Volume, Permeability
- **Physical Properties** (v0.5.31): Mass, Force, Pressure, Weight, Viscosity, Compressibility
- **Thermal** (v0.5.31): Temperature, TemperatureGradient
- **Rates & Ratios** (v0.5.31): Rate, Density, ProductivityIndex, custom ratios
- **Dimensionless** (v0.5.31): Percentage, fraction, ratio support
- **Energy** (v0.5.31): Power, Work, electrical measurements
- **Data** (v0.5.30): Bit and Byte with binary prefixes (KiB, MiB, GiB, etc.)
- **Date/Time** (v0.5.31): Calendar date conversions, time intervals

### 🎯 Special Conversions & Features

#### Oil & Gas Field Conversions
- Formation Volume Factor (FVF) support with `set_fvf()` and `get_fvf()`
- Density-based conversions with configurable default density
- Reservoir/standard volume conversions
- Temperature-corrected conversions

#### Date/Time Handling
- Calendar date conversions (identity conversion, no factor needed)
- Multiple date format support
- Special identity checks for date-to-date conversions

#### Compound Units
- Product units (kg*m, N*m, etc.)
- Ratio units (m/s, kg/m³, psi/ft, etc.)
- Power units (m², m³, ft², etc.)
- Nested compound support (kg*m²/s², etc.)

#### Prefix Combinations
- SI prefix application to base units (km, mm, µg, etc.)
- OGF (Oil & Gas Field) prefix system (MSCF, MMSCF, BSCF)
- Data storage prefixes (KB, MB, GB, KiB, MiB, GiB)
- Protected combinations prevent collisions

### 🔧 API Additions

#### Core Functions
- `units(value, units)` - Create Unit instance with proper type
- `convert(value, from_units, to_units)` - Direct value conversion
- `convertible(from_unit, to_unit)` - Check if conversion path exists
- `Unit` - Base class for isinstance() type checks
- `is_Unit(obj)` - Check if object is a Unit instance
- `valid_unit(unit_string)` - Validate unit string

#### Configuration Functions
- `set_fvf(value)` / `get_fvf()` - Formation volume factor management
- `set_density(value)` / `get_density()` - Default density configuration
- `print_path(enabled)` - Toggle conversion path display
- `verbose(level)` - Control logging verbosity
- `set_algorithm(name)` - Change search strategy ('BFS' or 'lean_BFS')
- `set_parallel(enabled)` - Enable/disable parallel processing
- `set_timeout(seconds)` - Configure search timeout
- `set_logging_level(level)` - Adjust log level

#### Cache Management Functions
- `save_memory()` - Persist conversion path cache to disk
- `load_memory()` - Restore cache from disk
- `clean_memory()` - Clear specific cache files
- `delete_cache()` - Remove all cache files
- `network_to_frame()` - Export network to pandas DataFrame

#### GUI Function
- `start_gui()` - Launch Tkinter GUI interface
- Command line: `python -m unyts` - Alternative GUI launch method

### 📊 Statistics

- **Version increment**: 0.9.15 → 0.10.1
- **Performance gain**: 200× faster imports, 78% faster rebuilds
- **Module versions updated**: 38 files with version tracking
- **Test modules**: 9+ comprehensive test files
- **Documentation pages**: 4+ optimization guides
- **Cache types**: 6 different specialized caches
- **Supported Python versions**: 3.7 through 3.11

---

## Version History Summary

### [0.10.1] - 2026-02-27
Major performance overhaul with lazy loading, comprehensive testing, and enhanced features.

### [0.10.0] - 2026-02-25
Performance optimizations and GUI improvements.

### Previous Versions (0.9.15 and earlier)
Pre-optimization baseline versions.

---

## Migration Guide from 0.9.15 to 0.10.1

### Breaking Changes
**None** - All changes are backward compatible. Existing code will continue to work without modifications.

### Recommended Updates

1. **Take advantage of faster imports**: Scripts that previously imported unyts can now start much faster.

2. **Update configuration**: New parameters available in `parameters.ini`:
   ```python
   from unyts import unyts_parameters_
   unyts_parameters_.max_generations_ = 25  # Adjust search depth
   unyts_parameters_.reduce_parentheses_ = True  # Simplify notation
   ```

3. **Use new validation features**:
   ```python
   from unyts import convertible
   if convertible('m', 'ft'):
       result = convert(100, 'm', 'ft')
   ```

4. **Enable lean BFS for faster searches** (already default):
   ```python
   from unyts import set_algorithm
   set_algorithm('lean_BFS')  # Default in 0.10.1
   ```

5. **Clear old caches** if upgrading:
   ```python
   from unyts import delete_cache
   delete_cache()  # Remove old cache files
   ```

### Performance Expectations

- **First import**: ~0.08s (down from ~14.5s)
- **First conversion**: ~14.5s database build + conversion time
- **Subsequent conversions**: Milliseconds (cached paths)
- **Subsequent imports** (same session): Instant (already loaded)
- **Subsequent imports** (new session): ~9s with cache (down from ~40s)

---

## Acknowledgments

This release represents a massive collaborative effort focused on performance optimization, testing infrastructure, and user experience improvements. Special thanks to all contributors who helped benchmark, test, and refine these enhancements.

---

## Links

- **Homepage**: https://github.com/ayaranitram/unyts
- **PyPI**: https://pypi.org/project/unyts/
- **Issue Tracker**: https://github.com/ayaranitram/unyts/issues
- **Documentation**: See README.md and USAGE.md
