#pragma once
// unyts/aliases.hpp — unit alias / alternate-name registry.
//
// This module manages the mapping from alias names (e.g. "metre", "m", "meters")
// to the canonical unit name used as a UNode in the conversion graph.
// It also tracks which units are simple numeric aliases (scale == true) vs.
// offset aliases.
//
// Phase 2: full data implementation.
// Phase 1: declarations only.

#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace unyts {

// ─── AliasEntry ───────────────────────────────────────────────────────────────
struct AliasEntry {
    std::string canonical;  // canonical node name in the graph
    double      factor;     // multiplicative scale (1.0 for exact aliases)
    bool        is_scale;   // true → pure scale alias; false → offset involved
};

// ─── AliasRegistry ────────────────────────────────────────────────────────────
class AliasRegistry {
public:
    // Register a simple synonym (exact name alias, factor == 1)
    void add_synonym(const std::string& alias, const std::string& canonical);

    // Register a scaled alias  (e.g. "km" == 1000 * "m")
    void add_scaled(const std::string& alias,
                    const std::string& canonical,
                    double factor);

    // Look up the canonical name; returns nullopt if not found
    std::optional<std::string> canonical(const std::string& alias) const;

    // Look up the full entry; returns nullptr if not found
    const AliasEntry* lookup(const std::string& alias) const;

    // All registered aliases
    std::vector<std::string> all_aliases() const;

    // Whether the name is a known alias (or canonical)
    bool is_known(const std::string& name) const;

private:
    std::unordered_map<std::string, AliasEntry> map_;
};

// Global singleton — populated by database.cpp during initialisation
AliasRegistry& global_alias_registry();

// Normalise a unit name to its canonical form, or return as-is if unknown
std::string normalize_unit(const std::string& name);

} // namespace unyts
