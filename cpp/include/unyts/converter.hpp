#pragma once
// unyts/converter.hpp — high-level conversion API.
//
// This header provides the top-level convert() and convertible() functions
// that the Python bindings (and any future Qt or C API layer) call.
// Internally these functions use:
//   1. AliasRegistry to normalise unit names,
//   2. the global UDigraph from database.hpp,
//   3. the search algorithms in graph.hpp (hybrid_BFS by default).
//
// Phase 2: full implementation including combined units (m/s, kg*m/s^2, …)
// Phase 1: simple single-unit conversion stub.

#include <optional>
#include <string>
#include <vector>

namespace unyts {

// ─── Result types ─────────────────────────────────────────────────────────────

struct ConversionResult {
    double      value;
    std::string from_unit;
    std::string to_unit;
    bool        exact;    // true when no floating-point rounding was needed
};

// ─── Core API ────────────────────────────────────────────────────────────────

/// Convert `value` from `from_unit` to `to_unit`.
/// Returns nullopt when no conversion path exists.
/// Throws std::invalid_argument for malformed unit strings.
std::optional<ConversionResult> convert(double value,
                                        const std::string& from_unit,
                                        const std::string& to_unit);

/// Return true when a conversion path between the two units exists.
bool convertible(const std::string& from_unit, const std::string& to_unit);

/// Return the numeric conversion factor (convert 1 from_unit → to_unit).
/// Returns nullopt when not convertible.
std::optional<double> conversion_factor(const std::string& from_unit,
                                        const std::string& to_unit);

/// Return a list of units that `from_unit` can be converted to.
std::vector<std::string> convertible_to(const std::string& from_unit);

// ─── Configuration ────────────────────────────────────────────────────────────

/// Set timeout for search algorithms in milliseconds (default 5000).
void set_search_timeout_ms(int ms);
int  get_search_timeout_ms();

} // namespace unyts
