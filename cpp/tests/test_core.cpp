// cpp/tests/test_core.cpp — C++ regression test suite for the unyts core engine.
//
// Mirrors the key assertions from:
//   tests/test_converter.py, test_network.py, test_searches.py,
//   test_dictionaries.py, test_units.py, test_density.py, test_parameters.py
//
// Build (MSVC):
//   Add CMakeLists.txt target 'unyts_tests' (see cpp/CMakeLists.txt)
// Run:
//   .\unyts_tests.exe
//
// No external test framework required — uses a minimal PASS/FAIL macro set.

#include "unyts/converter.hpp"
#include "unyts/database.hpp"
#include "unyts/graph.hpp"
#include "unyts/aliases.hpp"
#include "unyts/unyts_capi.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstring>
#include <iostream>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

// ─────────────────────────────────────────────────────────────────────────────
// Minimal test harness
// ─────────────────────────────────────────────────────────────────────────────

static int g_pass = 0, g_fail = 0;
static std::string g_section;

#define SECTION(name)  do { g_section = (name); \
    std::cout << "\n[" << g_section << "]\n"; } while(0)

#define CHECK(cond) \
    do { \
        if (cond) { std::cout << "  PASS  " << #cond << "\n"; ++g_pass; } \
        else       { std::cout << "  FAIL  " << #cond \
                               << "  (line " << __LINE__ << ")\n"; ++g_fail; } \
    } while(0)

#define CHECK_MSG(cond, msg) \
    do { \
        if (cond) { std::cout << "  PASS  " << (msg) << "\n"; ++g_pass; } \
        else       { std::cout << "  FAIL  " << (msg) \
                               << "  (line " << __LINE__ << ")\n"; ++g_fail; } \
    } while(0)

static bool near(double a, double b, double tol = 1e-4) {
    double denom = std::abs(b) > 1e-12 ? std::abs(b) : 1.0;
    return std::abs(a - b) / denom <= tol;
}

#define CHECK_NEAR(expr, expected, tol) \
    do { \
        double _got = (expr); \
        if (near(_got, (expected), (tol))) { \
            std::cout << "  PASS  " << #expr << "  =  " << _got << "\n"; ++g_pass; \
        } else { \
            std::cout << "  FAIL  " << #expr \
                      << "  got=" << _got << "  expected=" << (expected) << "\n"; ++g_fail; \
        } \
    } while(0)

#define CHECK_CONV(from_val, from_u, to_u, expected, tol) \
    do { \
        auto _r = unyts::convert((from_val), std::string(from_u), std::string(to_u)); \
        std::ostringstream _os; \
        _os << (from_val) << " " << (from_u) << " -> " << (to_u); \
        std::string _desc = _os.str(); \
        if (!_r) { \
            std::cout << "  FAIL  " << _desc << "  (no path)\n"; ++g_fail; \
        } else if (near(_r->value, (expected), (tol))) { \
            std::cout << "  PASS  " << _desc << "  =  " << _r->value << "\n"; ++g_pass; \
        } else { \
            std::cout << "  FAIL  " << _desc \
                      << "  got=" << _r->value << "  expected=" << (expected) << "\n"; ++g_fail; \
        } \
    } while(0)

#define CHECK_NO_PATH(from_u, to_u) \
    do { \
        auto _r = unyts::convert(1.0, std::string(from_u), std::string(to_u)); \
        std::string _desc = std::string(from_u) + " -> " + std::string(to_u) + " (expect no path)"; \
        if (!_r) { std::cout << "  PASS  " << _desc << "\n"; ++g_pass; } \
        else     { std::cout << "  FAIL  " << _desc << "  (got " << _r->value << ")\n"; ++g_fail; } \
    } while(0)

// ─────────────────────────────────────────────────────────────────────────────
// Test sections
// ─────────────────────────────────────────────────────────────────────────────

// ── Graph basics ──────────────────────────────────────────────────────────────
static void test_graph_basics() {
    SECTION("Graph basics");

    auto& g = unyts::global_graph();
    CHECK(g.has_node("meter"));
    CHECK(g.has_node("kg"));
    CHECK(g.has_node("second"));
    CHECK(!g.has_node("xyzzy__not_a_unit"));

    const auto names = unyts::all_unit_names();
    CHECK(names.size() > 1000);
    CHECK_MSG(unyts::is_known_unit("meter"),    "is_known_unit('meter')");
    CHECK_MSG(unyts::is_known_unit("km"),        "is_known_unit('km')");
    CHECK_MSG(!unyts::is_known_unit("notaunit"), "!is_known_unit('notaunit')");
}

// ── convertible() ─────────────────────────────────────────────────────────────
static void test_convertible() {
    SECTION("convertible()");

    CHECK(unyts::convertible("meter",    "foot"));
    CHECK(unyts::convertible("km",       "mile"));
    CHECK(unyts::convertible("kg",       "lb"));
    CHECK(unyts::convertible("Celsius",  "Fahrenheit"));
    CHECK(unyts::convertible("bara",     "psia"));
    CHECK(unyts::convertible("stb",      "m3"));
    CHECK(unyts::convertible("kWh",      "J"));
    CHECK(unyts::convertible("Darcy",    "mD"));
    CHECK(!unyts::convertible("meter",   "kg"));
    CHECK(!unyts::convertible("Celsius", "bar"));
    CHECK(!unyts::convertible("",        "meter"));
}

// ── Length ────────────────────────────────────────────────────────────────────
static void test_length() {
    SECTION("Length conversions");

    CHECK_CONV(1.0,    "km",    "m",        1000.0,       1e-6);
    CHECK_CONV(1.0,    "m",     "km",        0.001,        1e-6);
    CHECK_CONV(1.0,    "m",     "foot",      3.28084,      1e-4);
    CHECK_CONV(1.0,    "foot",  "m",         0.3048,       1e-6);
    CHECK_CONV(12.0,   "inch",  "foot",      1.0,          1e-6);
    CHECK_CONV(1.0,    "mile",  "km",        1.609344,     1e-6);
    CHECK_CONV(1.0,    "yard",  "meter",     0.9144,       1e-6);
    CHECK_CONV(1.0,    "nm",    "m",         1e-9,         1e-6);
    CHECK_CONV(1.0,    "metre", "meters",    1.0,          1e-6);  // alias
    CHECK_CONV(1.0,    "miles", "feet",      5280.0,       1e-4);  // plural alias
    CHECK_CONV(1.0,    "feet",  "inches",    12.0,         1e-6);
}

// ── Mass ──────────────────────────────────────────────────────────────────────
static void test_mass() {
    SECTION("Mass conversions");

    CHECK_CONV(1.0,    "kg",     "lb",       2.20462,      1e-4);
    CHECK_CONV(1.0,    "lb",     "kg",       0.453592,     1e-4);
    CHECK_CONV(1.0,    "ton",    "kg",       1016.047,     1e-4);   // long ton (UK)
    CHECK_CONV(1.0,    "tonne",  "kg",       1000.0,       1e-4);   // metric ton
    CHECK_CONV(1.0,    "g",      "mg",       1000.0,       1e-6);
    CHECK_CONV(1.0,    "oz",     "g",        28.3495,      1e-3);
    CHECK_CONV(1.0,    "short ton","lb",     2000.0,       1e-4);
    CHECK_CONV(1.0,    "long ton", "lb",     2240.0,       1e-4);
    CHECK_CONV(1.0,    "metric ton","kg",    1000.0,       1e-4);
    CHECK_CONV(1000.0, "kg",     "metric ton", 1.0,        1e-4);
}

// ── Temperature ───────────────────────────────────────────────────────────────
static void test_temperature() {
    SECTION("Temperature conversions");

    CHECK_CONV(100.0,  "C",          "F",       212.0,       1e-4);
    CHECK_CONV(212.0,  "F",          "C",       100.0,       1e-4);
    CHECK_CONV(0.0,    "C",          "K",       273.15,      1e-4);
    CHECK_CONV(273.15, "K",          "C",       0.0,         1e-3);
    CHECK_CONV(0.0,    "C",          "R",       491.67,      1e-3);
    CHECK_CONV(32.0,   "F",          "C",       0.0,         1e-4);
    CHECK_CONV(100.0,  "Celsius",    "Fahrenheit", 212.0,    1e-4);
    CHECK_CONV(100.0,  "degrees C",  "degrees F",  212.0,   1e-4);
    CHECK_CONV(0.0,    "Kelvin",     "Rankine", 0.0,         1e-4);  // 0 K = 0 R
}

// ── Pressure ──────────────────────────────────────────────────────────────────
static void test_pressure() {
    SECTION("Pressure conversions");

    CHECK_CONV(1.0,    "bara",  "psia",     14.5038,     1e-3);
    CHECK_CONV(1.0,    "psi",   "bar",      0.0689476,   1e-4);
    CHECK_CONV(1.0,    "atm",   "bara",     1.01325,     1e-4);
    CHECK_CONV(1.0,    "kPa",   "psi",      0.145038,    1e-4);
    CHECK_CONV(1.0,    "MPa",   "kPa",      1000.0,      1e-6);
    CHECK_CONV(1.0,    "psia",  "bara",     0.068948,    1e-3);
    CHECK_CONV(1.0,    "bar",   "Pa",       100000.0,    1e-4);
    CHECK_CONV(1.0,    "mmHg",  "Pa",       133.322,     1e-3);
}

// ── Volume ────────────────────────────────────────────────────────────────────
static void test_volume() {
    SECTION("Volume conversions");

    CHECK_CONV(1.0,    "stb",    "gallonUS", 42.0,        1e-4);
    CHECK_CONV(1.0,    "stb",    "m3",       0.158987,    1e-4);
    CHECK_CONV(1.0,    "m3",     "litre",    1000.0,      1e-4);
    CHECK_CONV(1.0,    "litre",  "mL",       1000.0,      1e-4);
    CHECK_CONV(1.0,    "ft3",    "litre",    28.3168,     1e-3);
    CHECK_CONV(1.0,    "gallonUS","litre",   3.78541,     1e-4);
    CHECK_CONV(1.0,    "scf",    "sm3",      0.0283168,   1e-4);
    CHECK_CONV(1.0,    "bbl",    "stb",      1.0,         1e-6);   // alias
    CHECK_CONV(1.0,    "cm3",    "mL",       1.0,         1e-6);
}

// ── Time ──────────────────────────────────────────────────────────────────────
static void test_time() {
    SECTION("Time conversions");

    CHECK_CONV(1.0,    "day",    "hour",     24.0,        1e-6);
    CHECK_CONV(1.0,    "year",   "day",      365.25,      1e-4);
    CHECK_CONV(1.0,    "minute", "second",   60.0,        1e-6);
    CHECK_CONV(1.0,    "hour",   "minute",   60.0,        1e-6);
    CHECK_CONV(1.0,    "week",   "day",      7.0,         1e-6);
    CHECK_CONV(1.0,    "days",   "hours",    24.0,        1e-6);   // plural alias
    CHECK_CONV(1.0,    "years",  "days",     365.25,      1e-4);   // plural alias
    CHECK_CONV(1.0,    "sec",    "millisecond", 1000.0,   1e-6);  // short alias
    CHECK_CONV(1.0,    "hr",     "min",      60.0,        1e-6);   // short alias
    CHECK_CONV(1.0,    "ms",     "s",        0.001,       1e-6);
    CHECK_CONV(1.0,    "ns",     "s",        1e-9,        1e-6);
}

// ── Energy ────────────────────────────────────────────────────────────────────
static void test_energy() {
    SECTION("Energy conversions");

    CHECK_CONV(1.0,    "kWh",   "J",        3600000.0,   1e-4);
    CHECK_CONV(1.0,    "kJ",    "BTU",      0.947817,    1e-4);
    CHECK_CONV(1.0,    "J",     "cal",      0.239006,    1e-4);
    CHECK_CONV(1.0,    "BTU",   "kJ",       1.05506,     1e-4);
    CHECK_CONV(1.0,    "kWh",   "MJ",       3.6,         1e-4);
}

// ── Density ───────────────────────────────────────────────────────────────────
static void test_density() {
    SECTION("Density conversions");

    CHECK_CONV(1.0,    "g/cm3", "kg/m3",   1000.0,       1e-4);
    CHECK_CONV(1.0,    "kg/m3", "g/cm3",   0.001,        1e-6);
    CHECK_CONV(1.0,    "lb/ft3","kg/m3",   16.0185,      1e-3);
    // API gravity
    CHECK_CONV(10.0,   "API",   "SgO",     1.0,          1e-3);   // 141.5/(131.5+10) = 1.0
    CHECK_CONV(1.0,    "g/cc",  "g/cm3",   1.0,          1e-6);   // alias
    // SgG to kg/m3
    CHECK_CONV(1.0,    "SgG",   "kg/m3",   1.225,        1e-3);
}

// ── Pressure gradient ─────────────────────────────────────────────────────────
static void test_pressure_gradient() {
    SECTION("Pressure gradient conversions");

    CHECK_CONV(1.0,    "psia/ft", "kPa/m",  22.6206,     1e-3);
    CHECK_CONV(1.0,    "psig/ft", "kPa/m",  22.6206,     1e-3);   // gauge gradient == absolute gradient
    CHECK_CONV(1.0,    "psi/ft",  "kPa/m",  22.6206,     1e-3);   // bare psi/ft same result
    CHECK_CONV(1.0,    "kPa/m",  "psia/ft", 0.044208,    1e-3);
    CHECK_CONV(1.0,    "bara/m", "kPa/m",   100.0,       1e-4);
    CHECK_CONV(50.0,   "lb/ft3", "psia/ft", 0.34722,     1e-3);   // 50/144
    CHECK_CONV(1000.0, "kg/m3",  "kPa/m",   9.807,       1e-3);   // 1 kg/m3 ≈ 0.00980665 kPa/m -> 1000 * 0.00980665 = 9.80665
}

// ── Viscosity ─────────────────────────────────────────────────────────────────
static void test_viscosity() {
    SECTION("Viscosity conversions");

    CHECK_CONV(1.0,    "cP",    "Pa*s",    0.001,        1e-6);
    CHECK_CONV(1.0,    "Pa*s",  "cP",      1000.0,       1e-4);
    CHECK_CONV(1.0,    "mPa*s", "cP",      1.0,          1e-6);
}

// ── Darcy / Permeability ──────────────────────────────────────────────────────
static void test_permeability() {
    SECTION("Permeability conversions");

    CHECK_CONV(1.0,    "Darcy", "mD",      1000.0,       1e-4);
    CHECK_CONV(1.0,    "mD",    "Darcy",   0.001,        1e-6);
    CHECK_CONV(1.0,    "D",     "mD",      1000.0,       1e-4);
}

// ── Speed ─────────────────────────────────────────────────────────────────────
static void test_speed() {
    SECTION("Speed conversions");

    CHECK_CONV(1.0,    "m/s",  "km/h",     3.6,          1e-4);
    CHECK_CONV(1.0,    "km/h", "m/s",      0.27778,      1e-3);
    CHECK_CONV(1.0,    "mph",  "km/h",     1.60934,      1e-4);
    CHECK_CONV(60.0,   "mph",  "ft/sec",   88.0,         1e-3);
    CHECK_CONV(1.0,    "kph",  "mph",      0.621371,     1e-4);
}

// ── Temperature gradient ──────────────────────────────────────────────────────
static void test_temperature_gradient() {
    SECTION("Temperature gradient conversions");

    CHECK_CONV(1.0,    "F/ft",  "C/m",     1.82269,      1e-4);
    CHECK_CONV(1.0,    "C/m",   "K/m",     1.0,          1e-6);  // 1:1 for delta
    CHECK_CONV(1.0,    "C/m",   "C/km",    1000.0,       1e-4);
    CHECK_CONV(1.0,    "F/ft",  "F/in",    0.08333,      1e-3);  // 1/12
    CHECK_CONV(1.0,    "F/ft",  "F/yd",    3.0,          1e-4);
    CHECK_CONV(1.0,    "F/ft",  "C/km",    1822.69,      1e-3);  // long chain
}

// ── Temperature rate of change ────────────────────────────────────────────────
static void test_temperature_rate() {
    SECTION("Temperature rate-of-change conversions");

    CHECK_CONV(1.0,    "C/min",  "C/hour",  60.0,        1e-4);
    CHECK_CONV(1.0,    "C/day",  "C/hour",  1.0/24.0,    1e-4);
    CHECK_CONV(1.0,    "C/min",  "F/min",   1.8,         1e-4);
    CHECK_CONV(1.0,    "F/min",  "F/s",     1.0/60.0,    1e-4);
}

// ── Case-insensitive lookup ────────────────────────────────────────────────────
static void test_ci_lookup() {
    SECTION("Case-insensitive unit lookup");

    // UPPERCASE forms that require CI resolution
    CHECK_CONV(1.0,    "KM",   "M",     1000.0, 1e-4);
    CHECK_CONV(1.0,    "KG",   "LB",    2.20462, 1e-3);
    CHECK_CONV(1.0,    "KWH",  "J",     3600000.0, 1e-4);
    CHECK_CONV(1.0,    "BARA", "PSIA",  14.5038, 1e-3);
    CHECK_CONV(1.0,    "STB",  "M3",    0.158987, 1e-4);
    CHECK_CONV(1.0,    "SCF",  "SM3",   0.0283168, 1e-4);
    CHECK_CONV(1.0,    "lb/ft3","LB/FT3", 1.0, 1e-6);  // mixed case self
}

// ── Alias resolution ──────────────────────────────────────────────────────────
static void test_aliases() {
    SECTION("Alias resolution");

    // Common alternate names
    CHECK_CONV(1.0, "metre",   "meter",  1.0,   1e-6);
    CHECK_CONV(1.0, "meters",  "meter",  1.0,   1e-6);
    CHECK_CONV(1.0, "litre",   "liter",  1.0,   1e-6);
    CHECK_CONV(1.0, "kilogram","kg",     1.0,   1e-6);
    CHECK_CONV(1.0, "kilograms","kg",    1.0,   1e-6);
    CHECK_CONV(1.0, "bbl",     "stb",   1.0,   1e-6);
    CHECK_CONV(1.0, "min",     "minute", 1.0,   1e-6);
    CHECK_CONV(1.0, "hr",      "hour",   1.0,   1e-6);
    CHECK_CONV(1.0, "sec",     "second", 1.0,   1e-6);
    CHECK_CONV(1.0, "cc",      "cm3",    1.0,   1e-6);
    CHECK_CONV(1.0, "mL",      "cm3",    1.0,   1e-6);
    CHECK_CONV(1.0, "ft",      "foot",   1.0,   1e-6);
    CHECK_CONV(1.0, "mi",      "mile",   1.0,   1e-6);
    CHECK_CONV(1.0, "in",      "inch",   1.0,   1e-6);
}

// ── Productivity units ────────────────────────────────────────────────────────
static void test_productivity() {
    SECTION("Productivity index conversions");

    CHECK_CONV(1.0, "stb/day/psi",  "sm3/day/bar", 2.30591,  1e-3);
    CHECK_CONV(1.0, "sm3/day/bar",  "stb/day/psi", 0.43367,  1e-3);
    CHECK_CONV(1.0, "stb/day/psia", "stb/day/psi", 1.0,      1e-6);
    CHECK_CONV(1.0, "sm3/day/kPa",  "sm3/day/bar", 100.0,    1e-4);

    // Generic compound fallback — units not pre-registered as graph nodes
    // 1 l/hr/Pa → sm3/day/psi:
    //   l→sm3 = 0.001, hr→day = 1/24, Pa→psi = 1/6894.757
    //   factor = 0.001 × 24 × 6894.757 ≈ 165.474
    CHECK_CONV(1.0, "l/hr/Pa",      "sm3/day/psi", 165.474,  1e-2);
    CHECK_CONV(1.0, "sm3/day/psi",  "l/hr/Pa",     1.0/165.474, 1e-6);
    // Generic rate: m/s ↔ km/h via compound decomposition (no explicit node needed)
    CHECK_CONV(1.0, "m/s",          "km/h",        3.6,      1e-4);

    // Reordered-token compound conversion (Pa and hr swapped vs canonical order)
    // l/Pa/hr → sm3/day/psi: same factor as l/hr/Pa → sm3/day/psi = 165.474
    CHECK_CONV(1.0, "l/Pa/hr",      "sm3/day/psi", 165.474,  1e-2);
    CHECK_CONV(1.0, "sm3/psi/day",  "l/Pa/hr",     1.0/165.474, 1e-6);
    // Reordered 3-token: m/kg/s → km/h/g (kg and s swapped relative to h/g in to)
    // positional fails: kg(-1) at pos-1 vs h(-1) (mass≠time)
    // best-fit: m→km(×0.001), kg(-1)→g(-1)(÷1000), s(-1)→h(-1)(÷1/3600=×3600) → 0.0036
    CHECK_CONV(1.0, "m/kg/s",       "km/h/g",      0.0036,   1e-6);

    // Same-dimension ratio: scf/stb → sm3/sm3 (GOR unit conversion)
    // Pass-1 positional must win: scf↔sm3(num), stb↔sm3(den)  — NOT cross-matched.
    // 1 scf/stb = (0.0283168 sm3)/(0.158987 sm3) ≈ 0.17811 sm3/sm3
    CHECK_CONV(1.0, "scf/stb",      "sm3/sm3",     0.17811,  1e-4);
    CHECK_CONV(1.0, "sm3/sm3",      "scf/stb",     1.0/0.17811, 1e-2);

    // Density → pressure gradient bridge via BFS (g/cc → kPa/m → MPa/km)
    // Correct physical value: 1 g/cc × g_earth = 9806.65 Pa/m = 9.807 MPa/km
    // (Note: Python gives 153.924 via a gauge-pressure artefact — that is a Python bug)
    CHECK_CONV(1.0, "g/cc",   "MPa/km",  9.807,   1e-3);
    CHECK_CONV(1.0, "MPa/km", "g/cc",    0.10197, 1e-4);
    CHECK_CONV(1.0, "g/cc",   "Pa/m",    9806.65, 1e-1);
    CHECK_CONV(1.0, "kg/m3",  "MPa/km",  0.009807, 1e-4);
}

// ── Power ─────────────────────────────────────────────────────────────────────
static void test_power() {
    SECTION("Power conversions");

    CHECK_CONV(1.0, "W",    "hp",   0.00134102, 1e-4);
    CHECK_CONV(1.0, "kW",   "W",    1000.0,     1e-4);
    CHECK_CONV(1.0, "hp",   "W",    745.7,      1e-3);
}

// ── Area ──────────────────────────────────────────────────────────────────────
static void test_area() {
    SECTION("Area conversions");

    CHECK_CONV(1.0, "m2",    "ft2",     10.7639,   1e-3);
    CHECK_CONV(1.0, "ft2",   "m2",      0.0929030, 1e-4);
    CHECK_CONV(1.0, "acre",  "m2",      4046.86,   1e-3);
    CHECK_CONV(1.0, "km2",   "m2",      1e6,       1e-4);
    CHECK_CONV(1.0, "sqft",  "ft2",     1.0,       1e-6);   // alias
    CHECK_CONV(1.0, "sq ft", "ft2",     1.0,       1e-6);   // alias with space
}

// ── No-path cases (different dimensions) ─────────────────────────────────────
static void test_no_path() {
    SECTION("No conversion path (incompatible dimensions)");

    CHECK_NO_PATH("meter",    "kg");
    CHECK_NO_PATH("Celsius",  "bar");
    CHECK_NO_PATH("second",   "meter");
    CHECK_NO_PATH("kWh",      "meter");
    CHECK_NO_PATH("lb/ft3",   "second");
}

// ── conversion_factor() ───────────────────────────────────────────────────────
static void test_conversion_factor() {
    SECTION("conversion_factor()");

    auto f = unyts::conversion_factor("km", "m");
    CHECK(f.has_value());
    CHECK_NEAR(*f, 1000.0, 1e-6);

    auto g2 = unyts::conversion_factor("kg", "lb");
    CHECK(g2.has_value());
    CHECK_NEAR(*g2, 2.20462, 1e-4);

    auto h = unyts::conversion_factor("meter", "kg");
    CHECK(!h.has_value());
}

// ── Timeout configuration ─────────────────────────────────────────────────────
static void test_timeout() {
    SECTION("Search timeout configuration");

    int orig = unyts::get_search_timeout_ms();
    unyts::set_search_timeout_ms(3000);
    CHECK(unyts::get_search_timeout_ms() == 3000);
    unyts::set_search_timeout_ms(orig);
    CHECK(unyts::get_search_timeout_ms() == orig);
}

// ── C API integration ─────────────────────────────────────────────────────────
static void test_capi_integration() {
    SECTION("C API integration");

    UnytsContext* ctx = unyts_create();
    CHECK(ctx != nullptr);

    double v = 0.0;
    CHECK(unyts_convert(ctx, 1.0, "km", "m", &v) == UNYTS_OK);
    CHECK_NEAR(v, 1000.0, 1e-6);

    CHECK(unyts_convertible(ctx, "kg", "lb") == 1);
    CHECK(unyts_convertible(ctx, "kg", "meter") == 0);

    CHECK(unyts_is_known_unit(ctx, "meter") == 1);
    CHECK(unyts_is_known_unit(ctx, "xyzzy") == 0);

    double f = 0.0;
    CHECK(unyts_conversion_factor(ctx, "ft", "m", &f) == UNYTS_OK);
    CHECK_NEAR(f, 0.3048, 1e-6);

    CHECK(unyts_convert(ctx, 1.0, "meter", "kg", &v) == UNYTS_ERR_NO_PATH);
    CHECK(unyts_convert(ctx, 1.0, nullptr, "m", &v) == UNYTS_ERR_BADARG);

    unyts_set_fvf(ctx, 1.1);
    CHECK(unyts_get_fvf(ctx) == 1.1);

    unyts_destroy(ctx);
    unyts_destroy(nullptr); // must not crash
    CHECK_MSG(true, "unyts_destroy(nullptr) no crash");
}

// ─────────────────────────────────────────────────────────────────────────────
// Performance benchmark
// ─────────────────────────────────────────────────────────────────────────────

struct BenchCase { const char* from; const char* to; double value; };

static void bench_conversions(int reps) {
    SECTION("Performance benchmark");

    static const BenchCase cases[] = {
        {"km",      "m",      1.0},
        {"kg",      "lb",     1.0},
        {"C",       "F",    100.0},
        {"bara",    "psia",   1.0},
        {"stb",     "m3",     1.0},
        {"kWh",     "J",      1.0},
        {"Darcy",   "mD",     1.0},
        {"cP",      "Pa*s",   1.0},
        {"lb/ft3",  "kg/m3",  1.0},
        {"F/ft",    "C/m",    1.0},
    };
    constexpr int N = static_cast<int>(sizeof(cases)/sizeof(cases[0]));

    // Warm up (ensures graph is loaded)
    for (int i = 0; i < N; ++i)
        unyts::convert(cases[i].value, cases[i].from, cases[i].to);

    auto t0 = std::chrono::steady_clock::now();
    volatile double sink = 0.0; // prevent dead-code elimination
    for (int r = 0; r < reps; ++r)
        for (int i = 0; i < N; ++i) {
            auto res = unyts::convert(cases[i].value, cases[i].from, cases[i].to);
            if (res) sink += res->value;
        }
    auto t1 = std::chrono::steady_clock::now();

    int total = reps * N;
    double ms  = std::chrono::duration<double, std::milli>(t1 - t0).count();
    double ns_each = ms * 1e6 / total;

    std::cout << "  Conversions: " << total << " in "
              << ms << " ms  ("
              << static_cast<int>(ns_each) << " ns/conversion)\n";
    // Informational only — not a hard pass/fail
    // (BFS without persistent in-process cache can take ~15ms for compound units)
    std::string note = ms < 5000.0 ? "fast" : "slow (consider enabling BFS cache)";
    std::cout << "  Benchmark note: " << note << "  (" << static_cast<int>(ms) << " ms total)\n";
    ++g_pass; // always counts as pass — it's benchmarking, not correctness
    (void)sink;
}

// ─────────────────────────────────────────────────────────────────────────────
int main()
{
    std::cout << "unyts C++ core test suite\n";
    std::cout << std::string(50, '=') << "\n";

    test_graph_basics();
    test_convertible();
    test_length();
    test_mass();
    test_temperature();
    test_pressure();
    test_volume();
    test_time();
    test_energy();
    test_density();
    test_pressure_gradient();
    test_viscosity();
    test_permeability();
    test_speed();
    test_temperature_gradient();
    test_temperature_rate();
    test_ci_lookup();
    test_aliases();
    test_productivity();
    test_power();
    test_area();
    test_no_path();
    test_conversion_factor();
    test_timeout();
    test_capi_integration();
    bench_conversions(1000);

    std::cout << "\n" << std::string(50, '=') << "\n";
    std::cout << "Result: " << g_pass << " passed, " << g_fail << " failed\n";
    return g_fail == 0 ? 0 : 1;
}
