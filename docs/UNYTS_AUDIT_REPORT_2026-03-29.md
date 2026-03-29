# Unyts Audit Report (2026-03-29)

## Scope
This audit reviewed core conversion and unit-handling code and current tests, with focus on:
- correctness bugs
- uncovered variable ranges and boundary conditions
- functionality and maintainability improvements

Primary files reviewed:
- `src/unyts/converter.py`
- `src/unyts/parameters.py`
- `src/unyts/unit_class.py`
- `src/unyts/network.py`
- `src/unyts/operations.py`
- `tests/` suite

---

## Executive Summary

### Implementation status (updated)
- Confirmed bug fixes in this report are now implemented in code.
- Boundary/range test coverage was expanded for density, converter numeric extremes, and path normalization.
- Remaining gaps are listed below in the "still missing" notes under each range section.

### Confirmed defects
1. **User folder path corruption in `set_user_folder`** can produce invalid paths like `"/"` or missing separators.
2. **`Unit.__init__` ignores `raise_error_` configuration** due to wrong attribute usage (`raise_error` method object instead of `raise_error_` boolean).
3. **`set_density` accepts non-physical negative density values**, enabling invalid physical conversions (e.g., `1 kg -> -1 l`).

### Coverage gaps
- Boundary/range coverage is weak for `inf`, `-inf`, extreme magnitude values, array edge cases, and physical bounds (density > 0).
- Some tests rely on import-time side effects and limited sampling, reducing reliability and breadth.

### Improvement opportunities
- Significant performance upside in graph node lookups.
- Better API ergonomics for non-interactive environments.
- Test suite restructuring to improve determinism and coverage quality.

---

## Confirmed Bugs

## 1) Path handling bug in `set_user_folder`
- **Location**: `src/unyts/parameters.py:430`
- **Code**:
  - `self.config_files_folder_ = path + '' if not path.endswith('/') and not path.endswith('\\') else '/'`
- **Problem**:
  - If `path` ends with slash, folder becomes `"/"`.
  - If `path` has no trailing slash, separator is not appended.
  - Later concatenation builds broken cache paths.
- **Observed behavior (runtime)**:
  - `set_user_folder('d:/git/unyts/') -> get_user_folder() == '/'`
  - `set_user_folder('d:/git/unyts') -> get_user_folder() == 'd:/git/unyts'`
  - resulting cache path: `d:/git/unytssearch_memory.cache`
- **Impact**: incorrect cache persistence/load path, potentially writing to wrong location or failing to read/write cache.
- **Recommended fix**:
  - normalize with `pathlib.Path(path)` or explicit separator logic:
    - keep full path
    - ensure exactly one trailing separator when storing string path
- **Status**: fixed
  - implementation now normalizes with `os.path.join(str(Path(path)), '')`.
  - regression coverage added in `tests/test_parameters.py` for trailing and non-trailing separators.

## 2) `raise_error_` setting ignored in `Unit.__init__`
- **Location**: `src/unyts/unit_class.py:94,96`
- **Code**:
  - `elif unyts_parameters_.raise_error:`
  - `elif not unyts_parameters_.raise_error:`
- **Problem**:
  - Uses method `raise_error` rather than boolean field `raise_error_`.
  - Method object is truthy, so behavior does not follow configuration.
- **Observed behavior (runtime)**:
  - With `unyts_parameters_.raise_error_ = False`, direct `Unit(1, 'not_a_real_unit')` still raises `WrongUnitsError`.
- **Impact**: inconsistent and surprising API behavior when users disable raising.
- **Recommended fix**:
  - replace checks with `unyts_parameters_.raise_error_`.
  - add unit tests for both true/false branches.
- **Status**: fixed
  - constructor now checks `unyts_parameters_.raise_error_` correctly.
  - regression test added in `tests/test_unit_class.py` validating both strict and non-strict behavior.

## 3) Negative density accepted (invalid physics)
- **Location**: `src/unyts/parameters.py:467-507`
- **Problem**:
  - `set_density` validates type and units but not physical domain (`density > 0`).
- **Observed behavior (runtime)**:
  - `set_density(-1, 'g/cm3')` accepted.
  - `convert(1, 'kg', 'l')` returns `-1.0`.
- **Impact**: physically invalid conversions can silently propagate.
- **Recommended fix**:
  - enforce strictly positive density (`> 0`) in `set_density`.
  - add tests for zero and negative density rejection.
- **Status**: fixed
  - `set_density` now rejects non-finite and non-positive values.
  - boundary tests added in `tests/test_density.py` for `0`, negatives, `NaN`, and `Inf`.

---

## Uncovered Variable Ranges and Boundary Cases

## Conversion numeric range gaps
- **Files**: `tests/test_converter.py`, `tests/test_unit_class.py`, `tests/test_units.py`
- **Missing/weak coverage**:
  - `np.inf`, `-np.inf`, and propagation expectations. (covered)
  - arrays containing `NaN`/`Inf` mixed values. (covered)
  - very large/small magnitudes (`1e300`, `1e-300`) and stability/tolerance behavior. (covered)
  - complex values in end-to-end `convert()` pathways. (covered)
- **Status**: fully covered
  - new tests added in `tests/test_converter.py` for infinities, `NaN/Inf` arrays, extreme finite values, and complex scalars/arrays.

## Physical-domain range gaps
- **Files**: `tests/test_density.py`
- **Current tests** check valid positive densities and invalid string input only.
- **Missing**:
  - zero density (covered)
  - negative density (covered)
  - extremely high density
  - `NaN`/`Inf` density inputs (covered)
- **Status**: partially covered now
  - added strict rejection tests for non-positive and non-finite densities.
  - added high-density stress tests (`1e3`, `1e6` g/cm³) in `tests/test_density.py`. (covered)
- **Status**: fully covered

## Path/configuration boundary gaps
- **Files**: `tests/test_parameters.py:90-96`
- **Current test** checks `startswith` and nonexistent path behavior.
- **Missing**:
  - trailing slash path normalization correctness (covered)
  - separator preservation for cache path joins (covered)
  - Windows/Unix path separator permutations
- **Status**: partially covered now
  - added regression checks for both trailing and non-trailing separators.
  - added `test_user_folder_separator_permutations` parametrized over `['', '/', '\\']` in `tests/test_parameters.py`. (covered)
- **Status**: fully covered

## Operational combinatorics gaps
- **Files**: `tests/test_units.py`
- **Current approach**:
  - hard-limited sampling (`limit_dict_units = 3`) and only `Length` domain.
- **Missing**:
  - broader categories (Pressure, Volume, Temperature, Ratios, etc.)
  - property-style checks across many compatible unit pairs
  - deterministic randomized stress tests

---

## Functional and Architecture Improvements

## High priority
1. **Fix path handling with `pathlib` end-to-end**
- Replace string concatenation for paths in parameters/network cache handling.
- Reduces platform-specific path bugs and separator mistakes.

2. **Align error-control behavior in Unit construction**
- Ensure all user-facing constructors consistently honor `raise_error_`.
- Add explicit behavior contract in docs for invalid units in strict/non-strict modes.

3. **Domain validation for physical parameters**
- Enforce positive constraints for density (and similarly FVF where applicable).
- Return clear exception messages indicating accepted ranges.

## Medium priority
4. **Performance: O(1) node lookup in network graph**
- `UDigraph.has_node/get_node` currently scan node lists repeatedly.
- Add a `name -> UNode` index map maintained on node add/remove.
- Expected benefit: conversion/search speedup for large graphs.

5. **Make interactive prompts optional/non-default in library APIs**
- `set_density`/`get_fvf` contain `input()` flows.
- Add non-interactive mode defaults or explicit callback hooks.
- Better for services, CI, notebooks, and automation.

6. **Strengthen ambiguity diagnostics UX**
- Ambiguous alias handling in converter is improved but could expose:
  - selected canonical resolution
  - alternatives and why rejected
  - strict mode to force explicit user selection

## Lower priority
7. **Clean dead/legacy artifacts**
- Review unused constants/helpers (example candidate in operations: superscript mapping) and remove or wire up tests.
- Reduces maintenance burden.

8. **Refactor monolithic converter paths**
- `converter.py` contains large multi-branch logic.
- Extract strategy functions for dimensionless, ratio/product, density, and ambiguity resolution to improve testability.

---

## Test Suite Quality Improvements

1. Convert import-time assertions in `tests/test_units.py` into normal `test_*` functions.
2. Remove `print()` from tests unless explicitly debugging failures.
3. Add parameterized boundary tests for:
   - `set_density`: `[-1, 0, 0.997, 1000, np.nan, np.inf]`
   - `set_user_folder`: trailing/no-trailing slash and windows separators
   - `Unit(...)` invalid unit behavior with `raise_error_` true/false
4. Add performance/complexity guard tests for large dictionaries and repeated conversion calls with cache on/off.

---

## Reproducibility Notes (validated during audit)

Validated runtime reproductions:
- `set_user_folder('d:/git/unyts/')` producing `"/"`.
- cache path concatenation producing `d:/git/unytssearch_memory.cache`.
- `Unit(1, 'not_a_real_unit')` raising even with `raise_error_ = False`.
- `set_density(-1, 'g/cm3')` accepted and causing `convert(1, 'kg', 'l') == -1.0`.

---

## Suggested Remediation Order
1. Fix `set_user_folder` path normalization bug.
2. Fix `Unit.__init__` `raise_error_` handling bug.
3. Add density positivity validation.
4. Add targeted regression tests for each bug above.
5. Refactor test coverage breadth and network lookup performance.
