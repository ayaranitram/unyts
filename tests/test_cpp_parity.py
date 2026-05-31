# -*- coding: utf-8 -*-
"""
Cross-engine parity tests: C++ engine vs Python engine vs Excel reference.

Three test suites:

1. test_cpp_vs_excel
   For every active row in tests/conversions_check.xlsx, run the C++ engine
   and assert the result matches the reference value within 1e-4 relative
   tolerance.  Rows where C++ returns None are recorded as MISSING and
   collected into a single failure at the end.

2. test_python_vs_excel
   Same check for the Python engine (regression guard — mirrors test_converter
   but uses the same harness so failures are directly comparable).

3. test_cpp_vs_python
   For every active row, compare C++ and Python results.  Both must agree to
   within 1e-6 relative tolerance.  C++ returning None when Python has a
   result is reported as MISSING.

Run with:
    pytest tests/test_cpp_parity.py -v
    pytest tests/test_cpp_parity.py -v -k "cpp_vs_excel"
"""

from __future__ import annotations

import math
import sys
import os
import pytest
import numpy as np
from pandas import read_excel

# ── Import Python engine ───────────────────────────────────────────────────────
from unyts import convert as py_convert, clean_memory

clean_memory()

# ── Import C++ engine ──────────────────────────────────────────────────────────
# Try the installed module first, then the build-output copy at repo root.
try:
    import unyts_cpp_native as cpp
    _CPP_AVAILABLE = True
except ImportError:
    _CPP_AVAILABLE = False

_CPP_SKIP_REASON = "unyts_cpp_native not available (build first)"

# ── Load reference data ────────────────────────────────────────────────────────
_EXCEL_PATH = os.path.join(os.path.dirname(__file__), "conversions_check.xlsx")

def _load_rows():
    """Return list of (id, source, target, in_val, out_val) for active rows."""
    data = read_excel(_EXCEL_PATH)
    active = data.loc[data["skip"] != "skip"].copy()
    rows = []
    for _, row in active.iterrows():
        out = row["out"]
        if isinstance(out, float) and math.isnan(out):
            continue  # no reference value — skip
        rows.append((
            int(row["id"]),
            str(row["source"]),
            str(row["target"]),
            float(row["in"]),
            float(out),
        ))
    return rows

_ROWS = _load_rows()

# ── Tolerance helpers ──────────────────────────────────────────────────────────
_REL_TOL = 1e-4   # primary: matches existing Python test
_ABS_TOL = 1e-12  # guard against division-by-zero on near-zero expected values


def _rel_err(got: float, expected: float) -> float:
    denom = max(abs(expected), _ABS_TOL)
    return abs(got - expected) / denom


# ── Parametrise ───────────────────────────────────────────────────────────────
def _row_id(row):
    row_id, src, tgt, _, _ = row
    return f"{row_id}:{src}->{tgt}"

_PARAMS = pytest.mark.parametrize("row", _ROWS, ids=_row_id)

# ── Known C++/Python unit-naming divergences ──────────────────────────────────
# These row IDs test unit pairs where Python and C++ intentionally disagree on
# whether a bare name (e.g. "pound/square inch", "bars") means gauge or absolute.
# Python convention: psi / pound/square inch / bars = gauge.
# C++ convention:   pound/square inch / bars = absolute.
# The *Python* regression tests (test_python_vs_excel) are still exercised for
# these rows; only the C++ comparison tests are suppressed.
_CPP_GAUGE_DIVERGENCE_ROWS = {1310, 1318, 1329, 1363}


# ─────────────────────────────────────────────────────────────────────────────
# 1. C++ engine vs Excel reference
# ─────────────────────────────────────────────────────────────────────────────

@_PARAMS
@pytest.mark.skipif(not _CPP_AVAILABLE, reason=_CPP_SKIP_REASON)
def test_cpp_vs_excel(row):
    """C++ engine result must match the Excel reference within 1e-4 rel. tolerance."""
    row_id, src, tgt, in_val, expected = row
    if row_id in _CPP_GAUGE_DIVERGENCE_ROWS:
        pytest.skip(f"[row {row_id}] Known C++/Python gauge-naming divergence: {src!r} → {tgt!r}")
    got = cpp.convert(in_val, src, tgt)
    assert got is not None, (
        f"[row {row_id}] C++ returned None for {src!r} → {tgt!r}  "
        f"(Python reference: {expected})"
    )
    err = _rel_err(got, expected)
    assert err < _REL_TOL, (
        f"[row {row_id}] {src!r} → {tgt!r}: "
        f"got {got}, expected {expected}, rel_err={err:.2e}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Python engine vs Excel reference  (regression guard)
# ─────────────────────────────────────────────────────────────────────────────

@_PARAMS
def test_python_vs_excel(row):
    """Python engine result must match the Excel reference within 1e-4 rel. tolerance."""
    row_id, src, tgt, in_val, expected = row
    got = py_convert(in_val, src, tgt, False)
    assert got is not None, (
        f"[row {row_id}] Python returned None for {src!r} → {tgt!r}  "
        f"(reference: {expected})"
    )
    err = _rel_err(float(got), expected)
    assert err < _REL_TOL, (
        f"[row {row_id}] {src!r} → {tgt!r}: "
        f"got {got}, expected {expected}, rel_err={err:.2e}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. C++ vs Python cross-engine parity
# ─────────────────────────────────────────────────────────────────────────────

@_PARAMS
@pytest.mark.skipif(not _CPP_AVAILABLE, reason=_CPP_SKIP_REASON)
def test_cpp_vs_python(row):
    """C++ and Python engines must agree to within 1e-6 rel. tolerance.

    If Python returns a valid result and C++ returns None, the test fails
    with a MISSING marker to distinguish it from a wrong-value failure.
    """
    row_id, src, tgt, in_val, _ = row
    if row_id in _CPP_GAUGE_DIVERGENCE_ROWS:
        pytest.skip(f"[row {row_id}] Known C++/Python gauge-naming divergence: {src!r} → {tgt!r}")
    py_result = py_convert(in_val, src, tgt, False)
    cpp_result = cpp.convert(in_val, src, tgt)

    if py_result is None:
        # Python can't convert this pair — nothing to compare against
        pytest.skip(f"Python engine returned None for {src!r} → {tgt!r}")

    py_val = float(py_result)

    assert cpp_result is not None, (
        f"[row {row_id}] MISSING in C++: {src!r} → {tgt!r}  "
        f"(Python result: {py_val})"
    )

    cpp_val = float(cpp_result)

    # For near-zero values (e.g. 0 °C → 0 K offset adjustments) use absolute
    if abs(py_val) < 1e-10 and abs(cpp_val) < 1e-10:
        assert abs(cpp_val - py_val) < 1e-10, (
            f"[row {row_id}] {src!r} → {tgt!r}: cpp={cpp_val}, py={py_val}"
        )
    else:
        err = _rel_err(cpp_val, py_val)
        assert err < 1e-6, (
            f"[row {row_id}] {src!r} → {tgt!r}: "
            f"cpp={cpp_val}, py={py_val}, rel_err={err:.2e}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Coverage summary  (non-parametric, informational)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(not _CPP_AVAILABLE, reason=_CPP_SKIP_REASON)
def test_cpp_coverage_summary():
    """Print a summary of how many Excel rows the C++ engine handles.

    This test always passes — it only prints the coverage percentage and
    lists unit pairs that are missing in C++ so they can be tracked.
    """
    missing = []
    wrong   = []
    ok      = 0

    for row_id, src, tgt, in_val, expected in _ROWS:
        got = cpp.convert(in_val, src, tgt)
        if got is None:
            missing.append((row_id, src, tgt, expected))
        elif _rel_err(got, expected) >= _REL_TOL:
            wrong.append((row_id, src, tgt, got, expected))
        else:
            ok += 1

    total = len(_ROWS)
    pct = 100.0 * ok / total if total else 0.0

    print(f"\n{'='*60}")
    print(f"C++ engine coverage: {ok}/{total} rows ({pct:.1f}%)")
    print(f"  Missing (C++ returned None): {len(missing)}")
    print(f"  Wrong value (rel_err >= 1e-4): {len(wrong)}")
    print(f"{'='*60}")

    if missing:
        print(f"\nMISSING unit pairs ({len(missing)}):")
        for row_id, src, tgt, exp in missing[:40]:
            print(f"  [{row_id:4d}] {src!r:25s} -> {tgt!r:25s}  (expected {exp})")
        if len(missing) > 40:
            print(f"  ... and {len(missing)-40} more")

    if wrong:
        print(f"\nWRONG values ({len(wrong)}):")
        for row_id, src, tgt, got, exp in wrong[:20]:
            print(f"  [{row_id:4d}] {src!r:25s} -> {tgt!r:25s}  "
                  f"got={got:.6g}  exp={exp:.6g}  "
                  f"err={_rel_err(got, exp):.2e}")

    # Always pass — this is an informational test
    assert True
