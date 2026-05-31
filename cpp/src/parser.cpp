// unyts/parser.cpp — full compound-unit expression parser (Phase 4).
//
// Handles expressions of the form:
//   "m"          → [{m, +1}]
//   "m/s"        → [{m, +1}, {s, -1}]
//   "kg*m/s^2"   → [{kg, +1}, {m, +1}, {s, -2}]
//   "ft^3/day"   → [{ft, +3}, {day, -1}]
//   "bbl/day"    → [{bbl, +1}, {day, -1}]
//
// Grammar (simplified, no parentheses):
//   expr  := token ( ('*'|'/') token )*
//   token := name ('^' integer)?
//   name  := any non-operator, non-whitespace characters
//
// After the first '/' operator all subsequent tokens are in the denominator,
// whether joined by '*' or '/'.  This matches the conventional oil-field
// notation where "sm3/d" and "stb/day/psi" are parsed left-to-right.

#include "unyts/parser.hpp"
#include "unyts/aliases.hpp"

#include <algorithm>
#include <cctype>
#include <stdexcept>
#include <string>

namespace unyts {

// ─── is_compound ─────────────────────────────────────────────────────────────

bool is_compound(const std::string& unit_str) {
    for (char c : unit_str)
        if (c == '*' || c == '/' || c == '^') return true;
    return false;
}

// ─── normalize_unit_string ───────────────────────────────────────────────────

std::string normalize_unit_string(const std::string& unit_str) {
    // Strip whitespace
    std::string stripped;
    stripped.reserve(unit_str.size());
    for (char c : unit_str)
        if (!std::isspace(static_cast<unsigned char>(c))) stripped += c;

    // Look up in alias registry for canonical name
    auto& reg = global_alias_registry();
    auto  canon = reg.canonical(stripped);
    return canon ? *canon : stripped;
}

// ─── parse_unit ──────────────────────────────────────────────────────────────

std::vector<UnitToken> parse_unit(const std::string& unit_str) {
    if (unit_str.empty()) return {};

    std::vector<UnitToken> result;
    bool in_denom = false;   // true after the first '/' is seen
    size_t i = 0;
    const size_t n = unit_str.size();

    while (i <= n) {
        // Collect characters until the next '*', '/', or end-of-string
        size_t j = i;
        while (j < n && unit_str[j] != '*' && unit_str[j] != '/') ++j;

        // Build the segment, stripping whitespace
        std::string seg;
        for (size_t k = i; k < j; ++k) {
            if (!std::isspace(static_cast<unsigned char>(unit_str[k])))
                seg += unit_str[k];
        }

        if (!seg.empty()) {
            // Split on '^'
            int         exp_mag   = 1;
            std::string unit_name = seg;
            size_t      caret     = seg.find('^');
            if (caret != std::string::npos) {
                unit_name = seg.substr(0, caret);
                const std::string exp_str = seg.substr(caret + 1);
                if (exp_str.empty()) return {};   // "m^" is malformed
                try {
                    exp_mag = std::stoi(exp_str);
                } catch (...) {
                    return {};                    // non-integer exponent
                }
                if (exp_mag <= 0 || exp_mag > 20) return {};  // sanity cap
            }

            if (unit_name.empty()) return {};

            int final_exp = in_denom ? -exp_mag : exp_mag;
            result.push_back({std::move(unit_name), final_exp});
        }

        // Advance past the operator
        if (j < n) {
            if (unit_str[j] == '/') in_denom = true;
            // '*' keeps the current numerator/denominator mode
        }
        i = j + 1;
    }

    return result;
}

} // namespace unyts
