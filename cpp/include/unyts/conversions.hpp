#pragma once
// unyts/conversions.hpp — declarations for all unit conversion functions.
//
// Each function is a direct port of the corresponding def in
// src/unyts/units/def_conversions.py.  Functions take a double and return a
// double.  They are used as ConvFn values when building the conversion graph.

#include "unyts/types.hpp"

namespace unyts {

// ── Physical constants ────────────────────────────────────────────────────────
inline constexpr double kStandardAirDensity    = 1.225;       // kg/m³
inline constexpr double kStandardEarthGravity  = 9.80665;     // m/s²
inline constexpr double kStandardWaterDensity  = 1.00;        // g/cm³
inline constexpr double kSpeedOfLight          = 299792458.0; // m/s

// ── Dimensionless / fraction ──────────────────────────────────────────────────
double equality(double x);
double inverse(double x);
double fraction__to__percentage(double x);
double percentage__to__fraction(double x);

// ── Time ─────────────────────────────────────────────────────────────────────
double second__to__millisecond(double t);
double minute__to__second(double t);
double hour__to__minute(double t);
double day__to__hour(double t);
double day__to__month(double t);
double week__to__day(double t);
double year__to__month(double t);
double year__to__day(double t);
double lustrum__to__year(double t);
double decade__to__year(double t);
double century__to__year(double t);
double nanosecond__to__second(double t);
double millisecond__to__second(double t);

// ── Temperature ───────────────────────────────────────────────────────────────
double Celsius__to__Kelvin(double t);
double Kelvin__to__Celsius(double t);
double Celsius__to__Fahrenheit(double t);
double Fahrenheit__to__Celsius(double t);
double Fahrenheit__to__Rankine(double t);
double Rankine__to__Fahrenheit(double t);
double Rankine__to__Kelvin(double t);
double Kelvin__to__Rankine(double t);

// ── Length ────────────────────────────────────────────────────────────────────
double yard__to__meter(double d);
double foot__to__meter(double d);
double inch__to__thou(double d);
double inch__to__tenth(double d);
double foot__to__inch(double d);
double yard__to__foot(double d);
double chain__to__yard(double d);
double furlong__to__chain(double d);
double mile__to__furlong(double d);
double league__to__mile(double d);
double nautical_league__to__nautical_mile(double d);
double nautical_mile__to__meter(double d);
double rod__to__yard(double d);
double astronomical_unit__to__meter(double d);
double parsec__to__astronomical_unit(double d);
double light_year__to__meter(double d);
double scandinavian_mile__to__kilometer(double d);

// ── Speed ─────────────────────────────────────────────────────────────────────
double mile_per_hour__to__kilometer_per_hour(double v);

// ── Area ──────────────────────────────────────────────────────────────────────
double square_kilometer__to__square_meter(double d);
double square_mile__to__acre(double d);
double acre__to__square_yard(double d);
double square_rod__to__square_yard(double d);
double square_yard__to__square_foot(double d);
double square_foot__to__square_inch(double d);
double square_foot__to__square_meter(double d);
double square_inch__to__square_thou(double d);
double square_inch__to__square_tenth(double d);
double square_chain__to__square_yard(double d);
double square_furlong__to__square_chain(double d);
double square_mile__to__square_furlong(double d);
double square_league__to__square_mile(double d);

// ── Permeability ──────────────────────────────────────────────────────────────
double Darcy__to__um2(double d);  // µm²

// ── Volume ────────────────────────────────────────────────────────────────────
double litre__to__cubic_centimeter(double v);
double gill__to__fluid_ounce(double v);
double pint__to__gill(double v);
double quart__to__pint(double v);
double gallonUS__to__fluid_ounce(double v);
double gallonUS__to__quart(double v);
double gallonUS__to__cubic_inch(double v);
double gallonUK__to__quartUK(double v);
double gallonUK__to__fluid_ounce_UK(double v);
double gallonUK__to__litre(double v);
double gillUK__to__fluid_ounce_UK(double v);
double pintUK__to__gillUK(double v);
double quartUK__to__pintUK(double v);
double cubic_foot__to__cubic_meter(double v);
double standard_cubic_foot__to__standard_cubic_meter(double v);
double standard_cubic_meter__to__standard_cubic_foot(double v);
double standard_barrel__to__USgal(double v);
double standard_cubic_meter__to__standard_barrel(double v);
double standard_barrel__to__standard_cubic_foot(double v);
double reservoir_cubic_meter__to__reservoir_barrel(double v);
double reservoir_cubic_meter__to__standard_cubic_meter(double v);  // requires FVF
double cubic_inch__to__cubic_thou(double v);
double cubic_inch__to__cubic_tenth(double v);
double cubic_foot__to__cubic_inch(double v);
double cubic_yard__to__cubic_foot(double v);
double cubic_chain__to__cubic_yard(double v);
double cubic_furlong__to__cubic_chain(double v);
double cubic_mile__to__cubic_furlong(double v);
double cubic_league__to__cubic_mile(double v);

// ── Pressure ──────────────────────────────────────────────────────────────────
double psi_gauge__to__absolute_psi(double p);
double absolute_psi__to__psi_gauge(double p);
double bar_gauge__to__absolute_bar(double p);
double absolute_bar__to__bar_gauge(double p);
double absolute_bar__to__absolute_psi(double p);
double bar_gauge__to__psi_gauge(double p);
double bar__to__psi(double p);
double psi__to__bar(double p);
double absolute_bar__to__Pascal(double p);
double atmosphere__to__Pascal(double p);
double atmosphere__to__Torr(double p);
double atmosphere__to__absolute_bar(double p);
double absolute_bar__to__kilogram_slash_square_centimeter(double p);

// ── Mass / Weight ─────────────────────────────────────────────────────────────
double grain__to__milligrams(double w);
double pennyweight__to__grain(double w);
double dram__to__pound(double w);
double stone__to__pound(double w);
double quarter__to__stone(double w);
double weight_ounce__to__dram(double w);
double pound__to__weight_ounce(double w);
double long_hundredweight__to__quarter(double w);
double short_hundredweight__to__pound(double w);
double short_ton__to__short_hundredweight(double w);
double long_ton__to__long_hundredweight(double w);
double metric_ton__to__kilogram(double w);
double kilogram__to__gram(double w);
double pound__to__kilogram(double w);
double pound__to__gram(double w);

// ── Force ─────────────────────────────────────────────────────────────────────
double kilogram_mass__to__kilogram_force(double f);
double kilogram_force__to__kilogram_mass(double f);
double kilogram_force__to__Newton(double f);
double Dyne__to__Newton(double f);
double Newton__to__Dyne(double f);

// ── Energy ────────────────────────────────────────────────────────────────────
double Joule__to__gram_calorie(double e);
double Kilojoule__to__Joule(double e);
double Kilojoule__to__kilowatt_hour(double e);
double Kilojoule__to__British_thermal_unit(double e);
double British_thermal_unit__to__Joule(double e);
double kilowatt_hour__to__Kilojoule(double e);
double Watt_second__to__Joule(double e);
double Watt_hour__to__Kilojoule(double e);

// ── Power ─────────────────────────────────────────────────────────────────────
double Horsepower__to__Watt(double p);

// ── Velocity ──────────────────────────────────────────────────────────────────
double kilometer_per_hour__to__meter_per_second(double v);

// ── Viscosity ─────────────────────────────────────────────────────────────────
double centipoise__to__Poise(double v);
double Poise__to__Pascal_second(double v);

// ── FVF-dependent conversions (called via the global FVF) ────────────────────
// These wrap reservoir_cubic_meter__to__standard_cubic_meter at the call site.
// The ConvFn lambda captures the FVF at graph-build time or calls global_fvf().

} // namespace unyts
