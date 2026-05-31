#pragma once
// unyts/parser.hpp — unit string parser.
//
// Parses compound unit expressions such as "m/s", "kg*m/s^2", "bbl/day"
// into a list of (unit_name, exponent) tokens that the converter can then
// look up in the graph.
//
// Phase 2: full implementation supporting multiplication, division, powers.
// Phase 1: minimal stub.

#include <string>
#include <vector>

namespace unyts {

// ─── Token ────────────────────────────────────────────────────────────────────
struct UnitToken {
    std::string name;       // canonical (or raw) unit name
    int         exponent;   // +1 for numerator, -1 for denominator, ±N for powers
};

// ─── Parser ───────────────────────────────────────────────────────────────────

/// Parse a compound unit string into its constituent tokens.
/// Examples:
///   "m"        → [{name:"m", exp:1}]
///   "m/s"      → [{name:"m", exp:1}, {name:"s", exp:-1}]
///   "kg*m/s^2" → [{name:"kg", exp:1}, {name:"m", exp:1}, {name:"s", exp:-2}]
/// Returns an empty vector when the string cannot be parsed.
std::vector<UnitToken> parse_unit(const std::string& unit_str);

/// Return true if the string contains a compound expression (*, /, ^).
bool is_compound(const std::string& unit_str);

/// Normalise a unit string: strip whitespace, lowercase, canonical aliases.
/// e.g. "Metres / Second" → "m/s"
std::string normalize_unit_string(const std::string& unit_str);

} // namespace unyts
