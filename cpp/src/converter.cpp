// unyts/converter.cpp — high-level convert / convertible API (Phase 1 stub).

#include "unyts/converter.hpp"
#include "unyts/aliases.hpp"
#include "unyts/database.hpp"
#include "unyts/graph.hpp"
#include "unyts/parser.hpp"
#include <algorithm>
#include <cctype>
#include <cmath>

namespace unyts {

// ─── Timeout configuration ────────────────────────────────────────────────────
static int g_timeout_ms = 5000;

void set_search_timeout_ms(int ms) { g_timeout_ms = ms; }
int  get_search_timeout_ms()       { return g_timeout_ms; }

// ─── Internal helpers ────────────────────────────────────────────────────────

static std::string resolve_name(const std::string& unit) {
    // 1. exact alias registry lookup
    std::string canonical = normalize_unit(unit);
    if (global_graph().has_node(canonical)) return canonical;

    // 2. lowercase fallback through alias registry
    //    Only use when the registry explicitly maps to a *different* canonical
    //    (avoids mistakenly returning a direct node like msm3 for MSM3)
    std::string lower = unit;
    std::transform(lower.begin(), lower.end(), lower.begin(),
                   [](unsigned char c){ return std::tolower(c); });
    if (lower != unit) {
        std::string lower_canon = normalize_unit(lower);
        if (lower_canon != lower && global_graph().has_node(lower_canon)) return lower_canon;
    }

    // 3. case-insensitive linear scan over all graph node names.
    //    Only resolve if exactly ONE node matches (avoids ambiguous matches
    //    like Msm3 vs msm3 where prefix case is significant).
    {
        std::string found;
        int matches = 0;
        for (const auto& name : global_graph().list_nodes()) {
            std::string n_lower = name;
            std::transform(n_lower.begin(), n_lower.end(), n_lower.begin(),
                           [](unsigned char c){ return std::tolower(c); });
            if (n_lower == lower) {
                if (++matches > 1) { found.clear(); break; }
                found = name;
            }
        }
        if (!found.empty()) return found;
    }

    return unit; // not found; BFS will return nullopt
}

static const UNode* resolve_node(const std::string& unit) {
    std::string name = resolve_name(unit);
    return global_graph().get_node(name);
}

// ─── Compound-unit conversion fallback ──────────────────────────────────────
// Two-pass strategy (mirrors Python's behaviour):
//   Pass 1 — positional: try token[i] ↔ token[i] for every i.  If all pairs
//             match this is the preferred result (safe for same-dimension ratios
//             like scf/stb → sm3/sm3 where cross-pairing would be wrong).
//   Pass 2 — greedy best-fit: for each from-token, try every unmatched to-token
//             in order, requiring matching exponents.  Only runs when positional
//             fails (e.g. l/Pa/hr → sm3/day/psi, where Pa≠day positionally).
// Exponent pre-filter is applied in both passes: only tokens with matching
// exponents can be paired, preventing numerator↔denominator cross-matching.

static std::optional<double> try_atom_factor(const UnitToken& ft,
                                              const UnitToken& tt)
{
    if (ft.exponent != tt.exponent) return std::nullopt;
    if (ft.name == tt.name) return 1.0;          // identical atom

    auto atom1 = convert(1.0, ft.name, tt.name);
    if (!atom1) return std::nullopt;

    // Use the slope (differential) of the conversion rather than the absolute
    // value at 1.  For purely multiplicative conversions f(0)=0 so this is
    // a no-op.  For affine conversions (gauge pressure: psig→kPa adds ~101 kPa;
    // temperature: °C→K adds 273.15) the offset is subtracted so that compound
    // ratio units (e.g. psig/ft → kPa/m) use the correct gradient, not the
    // offset-inflated absolute value (355 kPa/m instead of 22.62 kPa/m).
    double f = atom1->value;
    auto atom0 = convert(0.0, ft.name, tt.name);
    if (atom0) f -= atom0->value;   // slope = f(1) - f(0)

    const int exp = ft.exponent;
    if      (exp ==  1) return f;
    else if (exp == -1) return 1.0 / f;
    else                return std::pow(f, static_cast<double>(exp));
}

static std::optional<ConversionResult> convert_compound(
        double value,
        const std::string& from_unit,
        const std::string& to_unit)
{
    auto from_toks = parse_unit(from_unit);
    auto to_toks   = parse_unit(to_unit);

    if (from_toks.empty() || to_toks.empty())  return std::nullopt;
    if (from_toks.size()  != to_toks.size())   return std::nullopt;

    const size_t n = from_toks.size();

    // ── Pass 1: positional (i → i) ──────────────────────────────────────────
    {
        double factor = 1.0;
        bool   ok     = true;
        for (size_t i = 0; i < n; ++i) {
            auto f = try_atom_factor(from_toks[i], to_toks[i]);
            if (!f) { ok = false; break; }
            factor *= *f;
        }
        if (ok) return ConversionResult{value * factor, from_unit, to_unit, false};
    }

    // ── Pass 2: greedy best-fit (handles reordered tokens) ──────────────────
    {
        std::vector<bool> used(n, false);
        double factor = 1.0;

        for (size_t i = 0; i < n; ++i) {
            bool matched = false;
            for (size_t j = 0; j < n; ++j) {
                if (used[j]) continue;
                auto f = try_atom_factor(from_toks[i], to_toks[j]);
                if (!f) continue;
                factor  *= *f;
                used[j]  = true;
                matched  = true;
                break;
            }
            if (!matched) return std::nullopt;
        }
        return ConversionResult{value * factor, from_unit, to_unit, false};
    }
}

// ─── convert ─────────────────────────────────────────────────────────────────

std::optional<ConversionResult> convert(double value,
                                        const std::string& from_unit,
                                        const std::string& to_unit) {
    const UNode* src = resolve_node(from_unit);
    const UNode* dst = resolve_node(to_unit);
    if (src && dst) {
        if (*src == *dst) return ConversionResult{value, from_unit, to_unit, true};

        UDigraph& g   = global_graph();
        TimePoint dlm = make_deadline(g_timeout_ms);

        auto path = hybrid_BFS(g, *src, *dst, dlm);
        if (path)
            return ConversionResult{apply_path(g, *path, value), from_unit, to_unit, false};
    }

    // Fall back to generic compound decomposition
    if (is_compound(from_unit) || is_compound(to_unit))
        return convert_compound(value, from_unit, to_unit);

    return std::nullopt;
}

// ─── convertible ─────────────────────────────────────────────────────────────

bool convertible(const std::string& from_unit, const std::string& to_unit) {
    const UNode* src = resolve_node(from_unit);
    const UNode* dst = resolve_node(to_unit);
    if (src && dst) {
        if (*src == *dst) return true;
        UDigraph& g   = global_graph();
        TimePoint dlm = make_deadline(g_timeout_ms);
        if (hybrid_BFS(g, *src, *dst, dlm)) return true;
    }

    // Fall back to generic compound decomposition
    if (is_compound(from_unit) || is_compound(to_unit))
        return convert_compound(1.0, from_unit, to_unit).has_value();

    return false;
}

// ─── conversion_factor ───────────────────────────────────────────────────────

std::optional<double> conversion_factor(const std::string& from_unit,
                                        const std::string& to_unit) {
    auto result = convert(1.0, from_unit, to_unit);
    if (!result) return std::nullopt;
    return result->value;
}

// ─── convertible_to ──────────────────────────────────────────────────────────

std::vector<std::string> convertible_to(const std::string& from_unit) {
    const UNode* src = resolve_node(from_unit);
    if (!src) return {};

    UDigraph& g = global_graph();
    std::vector<std::string> result;
    for (const auto& name : g.list_nodes()) {
        if (name == src->name) continue;
        const UNode* dst = g.get_node(name);
        if (!dst) continue;
        TimePoint dlm = make_deadline(g_timeout_ms);
        if (hybrid_BFS(g, *src, *dst, dlm)) result.push_back(name);
    }
    return result;
}

} // namespace unyts
