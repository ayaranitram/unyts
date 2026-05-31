// unyts/conversions.cpp — all unit conversion functions.
//
// Direct port of src/unyts/units/def_conversions.py.
// Each function is a pure double → double transformation.

#include "unyts/conversions.hpp"
#include <cmath>

namespace unyts {

// ── Dimensionless / fraction ──────────────────────────────────────────────────
double equality(double x)                     { return x; }
double inverse(double x)                      { return 1.0 / x; }
double fraction__to__percentage(double x)     { return x * 100.0; }
double percentage__to__fraction(double x)     { return x / 100.0; }

// ── Time ─────────────────────────────────────────────────────────────────────
double nanosecond__to__second(double t)       { return t * 1e-9; }
double millisecond__to__second(double t)      { return t * 1e-3; }
double second__to__millisecond(double t)      { return t * 1000.0; }
double minute__to__second(double t)           { return t * 60.0; }
double hour__to__minute(double t)             { return t * 60.0; }
double day__to__hour(double t)                { return t * 24.0; }
double day__to__month(double t)               { return t / 365.25 * 12.0; }
double week__to__day(double t)                { return t * 7.0; }
double year__to__month(double t)              { return t * 12.0; }
double year__to__day(double t)                { return t * 36525.0 / 100.0; }
double lustrum__to__year(double t)            { return t * 5.0; }
double decade__to__year(double t)             { return t * 10.0; }
double century__to__year(double t)            { return t * 100.0; }

// ── Temperature ───────────────────────────────────────────────────────────────
double Celsius__to__Kelvin(double t)          { return t + 273.15; }
double Kelvin__to__Celsius(double t)          { return t - 273.15; }
double Celsius__to__Fahrenheit(double t)      { return t * 9.0 / 5.0 + 32.0; }
double Fahrenheit__to__Celsius(double t)      { return (t - 32.0) * 5.0 / 9.0; }
double Fahrenheit__to__Rankine(double t)      { return t + 459.67; }
double Rankine__to__Fahrenheit(double t)      { return t - 459.67; }
double Rankine__to__Kelvin(double t)          { return t * 5.0 / 9.0; }
double Kelvin__to__Rankine(double t)          { return t * 9.0 / 5.0; }

// ── Length ────────────────────────────────────────────────────────────────────
double yard__to__meter(double d)              { return d * 9144.0 / 10000.0; }
double foot__to__meter(double d)              { return d * 3048.0 / 10000.0; }
double inch__to__thou(double d)               { return d * 1000.0; }
double inch__to__tenth(double d)              { return d * 10.0; }
double foot__to__inch(double d)               { return d * 12.0; }
double yard__to__foot(double d)               { return d * 3.0; }
double chain__to__yard(double d)              { return d * 22.0; }
double furlong__to__chain(double d)           { return d * 10.0; }
double mile__to__furlong(double d)            { return d * 8.0; }
double league__to__mile(double d)             { return d * 3.0; }
double nautical_league__to__nautical_mile(double d) { return d * 3.0; }
double nautical_mile__to__meter(double d)     { return d * 1852.0; }
double rod__to__yard(double d)                { return d * 55.0 / 10.0; }
double astronomical_unit__to__meter(double d) { return d * 149597870700.0; }
double parsec__to__astronomical_unit(double d){ return d * 206265.0; }
double light_year__to__meter(double d)        { return d * kSpeedOfLight * 365.25 * 24.0 * 60.0 * 60.0; }
double scandinavian_mile__to__kilometer(double d) { return d * 10.0; }

// ── Speed ─────────────────────────────────────────────────────────────────────
// Python: v * 8 * 10 * 22 * 9144 / 10000 / 1000
// = v * (mile_in_yards * yard_in_meters) / 1000  → km/h
double mile_per_hour__to__kilometer_per_hour(double v) {
    return v * 8.0 * 10.0 * 22.0 * 9144.0 / 10000.0 / 1000.0;
}
double kilometer_per_hour__to__meter_per_second(double v) { return v / 3.6; }

// ── Area ──────────────────────────────────────────────────────────────────────
double square_kilometer__to__square_meter(double d)  { return d * 1'000'000.0; }
double square_mile__to__acre(double d)               { return d * 640.0; }
double acre__to__square_yard(double d)               { return d * 4840.0; }
double square_rod__to__square_yard(double d)         { return d * 3025.0 / 100.0; }
double square_yard__to__square_foot(double d)        { return d * 9.0; }
double square_foot__to__square_inch(double d)        { return d * 144.0; }
double square_foot__to__square_meter(double d)       { return d * (3048.0 * 3048.0) / (10000.0 * 10000.0); }
double square_inch__to__square_thou(double d)        { return d * 1'000'000.0; }
double square_inch__to__square_tenth(double d)       { return d * 100.0; }
double square_chain__to__square_yard(double d)       { return d * (22.0 * 22.0); }
double square_furlong__to__square_chain(double d)    { return d * (10.0 * 10.0); }
double square_mile__to__square_furlong(double d)     { return d * (8.0 * 8.0); }
double square_league__to__square_mile(double d)      { return d * (3.0 * 3.0); }

// ── Permeability ──────────────────────────────────────────────────────────────
double Darcy__to__um2(double d)  { return d * 0.9869233; }

// ── Volume ────────────────────────────────────────────────────────────────────
double litre__to__cubic_centimeter(double v)                    { return v * 1000.0; }
double gill__to__fluid_ounce(double v)                          { return v * 4.0; }
double pint__to__gill(double v)                                 { return v * 4.0; }
double quart__to__pint(double v)                                { return v * 2.0; }
double gallonUS__to__fluid_ounce(double v)                      { return v * 128.0; }
double gallonUS__to__quart(double v)                            { return v * 4.0; }
double gallonUS__to__cubic_inch(double v)                       { return v * 231.0; }
double gallonUK__to__quartUK(double v)                          { return v * 4.0; }
double gallonUK__to__fluid_ounce_UK(double v)                   { return v * 160.0; }
double gallonUK__to__litre(double v)                            { return v * 4.54609; }
double gillUK__to__fluid_ounce_UK(double v)                     { return v * 4.0; }
double pintUK__to__gillUK(double v)                             { return v * 4.0; }
double quartUK__to__pintUK(double v)                            { return v * 2.0; }
double cubic_foot__to__cubic_meter(double v)                    { return v * std::pow(3048.0, 3) / std::pow(10000.0, 3); }
double standard_cubic_foot__to__standard_cubic_meter(double v)  { return v * std::pow(3048.0, 3) / std::pow(10000.0, 3); }
double standard_cubic_meter__to__standard_cubic_foot(double v)  { return v / std::pow(3048.0, 3) * std::pow(10000.0, 3); }
double standard_barrel__to__USgal(double v)                     { return v * 42.0; }
double standard_cubic_meter__to__standard_barrel(double v)      { return v * 6.289814; }
double standard_barrel__to__standard_cubic_foot(double v)       { return v * 5.614584; }
double reservoir_cubic_meter__to__reservoir_barrel(double v)    { return v * 6.289814; }
// FVF-dependent: implemented in database.cpp via a capturing lambda
double reservoir_cubic_meter__to__standard_cubic_meter(double /*v*/) { return 0.0; /* placeholder */ }
double cubic_inch__to__cubic_thou(double v)                     { return v * std::pow(1000.0, 3); }
double cubic_inch__to__cubic_tenth(double v)                    { return v * std::pow(10.0, 3); }
double cubic_foot__to__cubic_inch(double v)                     { return v * std::pow(12.0, 3); }
double cubic_yard__to__cubic_foot(double v)                     { return v * std::pow(3.0, 3); }
double cubic_chain__to__cubic_yard(double v)                    { return v * std::pow(22.0, 3); }
double cubic_furlong__to__cubic_chain(double v)                 { return v * std::pow(10.0, 3); }
double cubic_mile__to__cubic_furlong(double v)                  { return v * std::pow(8.0, 3); }
double cubic_league__to__cubic_mile(double v)                   { return v * std::pow(3.0, 3); }

// ── Pressure ──────────────────────────────────────────────────────────────────
double psi_gauge__to__absolute_psi(double p)                            { return p + 14.6959; }
double absolute_psi__to__psi_gauge(double p)                            { return p - 14.6959; }
double bar_gauge__to__absolute_bar(double p)                            { return p + 1.01325; }
double absolute_bar__to__bar_gauge(double p)                            { return p - 1.01325; }
double absolute_bar__to__absolute_psi(double p)                         { return p * 14.50377377322; }
double bar_gauge__to__psi_gauge(double p)                               { return p * 14.50377377322; }
double bar__to__psi(double p)                                           { return p * 14.50377377322; }
double psi__to__bar(double p)                                           { return p / 14.50377377322; }
double absolute_bar__to__Pascal(double p)                               { return p * 100000.0; }
double atmosphere__to__Pascal(double p)                                 { return p * 101325.0; }
double atmosphere__to__Torr(double p)                                   { return p * 760.0; }
double atmosphere__to__absolute_bar(double p)                           { return p * 101325.0 / 100000.0; }
double absolute_bar__to__kilogram_slash_square_centimeter(double p)     { return p * (10.0 / kStandardEarthGravity); }

// ── Mass / Weight ─────────────────────────────────────────────────────────────
double grain__to__milligrams(double w)              { return w * 64.7989; }
double pennyweight__to__grain(double w)             { return w * 24.0; }
double dram__to__pound(double w)                    { return w / 256.0; }
double stone__to__pound(double w)                   { return w * 14.0; }
double quarter__to__stone(double w)                 { return w * 2.0; }
double weight_ounce__to__dram(double w)             { return w * 16.0; }
double pound__to__weight_ounce(double w)            { return w * 16.0; }
double long_hundredweight__to__quarter(double w)    { return w * 4.0; }
double short_hundredweight__to__pound(double w)     { return w * 100.0; }
double short_ton__to__short_hundredweight(double w) { return w * 20.0; }
double long_ton__to__long_hundredweight(double w)   { return w * 20.0; }
double metric_ton__to__kilogram(double w)           { return w * 1000.0; }
double kilogram__to__gram(double w)                 { return w * 1000.0; }
double pound__to__kilogram(double w)                { return w * 45359237.0 / 100000000.0; }
double pound__to__gram(double w)                    { return w * 45359237.0 / 100000.0; }

// ── Force ─────────────────────────────────────────────────────────────────────
double kilogram_mass__to__kilogram_force(double f)  { return f * kStandardEarthGravity; }
double kilogram_force__to__kilogram_mass(double f)  { return f / kStandardEarthGravity; }
double kilogram_force__to__Newton(double f)         { return f * kStandardEarthGravity; }
double Dyne__to__Newton(double f)                   { return f * 1e-5; }
double Newton__to__Dyne(double f)                   { return f * 1e5; }

// ── Energy ────────────────────────────────────────────────────────────────────
double Joule__to__gram_calorie(double e)            { return e / 4.184; }
double Kilojoule__to__Joule(double e)               { return e * 1000.0; }
double Kilojoule__to__kilowatt_hour(double e)       { return e / 3600.0; }
double Kilojoule__to__British_thermal_unit(double e){ return e / 1.055; }
double British_thermal_unit__to__Joule(double e)    { return e * 1055.0; }
double kilowatt_hour__to__Kilojoule(double e)       { return e * 3600.0; }
double Watt_second__to__Joule(double e)             { return e; }         // 1 W·s == 1 J
double Watt_hour__to__Kilojoule(double e)           { return e * 3.6; }

// ── Power ─────────────────────────────────────────────────────────────────────
double Horsepower__to__Watt(double p)               { return p * 745.69987; }

// ── Viscosity ─────────────────────────────────────────────────────────────────
double centipoise__to__Poise(double v)              { return v / 100.0; }
double Poise__to__Pascal_second(double v)           { return v / 10.0; }

} // namespace unyts
