#pragma once
// unyts/database.hpp — unit registry and graph population.
//
// This is the data layer: it defines all supported units, their conversion
// factors, and aliases, and populates a UDigraph with the corresponding edges.
//
// Phase 2: full unit data ported from Python dictionaries.
// Phase 1: minimal stub that lets the project compile.

#include <string>
#include <vector>

namespace unyts {

class UDigraph;
class AliasRegistry;

// ─── Initialisation ────────────────────────────────────────────────────────

/// Populate `graph` with all known unit nodes and conversion edges.
/// Also populates the global AliasRegistry.
/// Should be called once at startup.
void populate_graph(UDigraph& graph);

/// Return (and lazily initialise) the global singleton conversion graph.
UDigraph& global_graph();

/// Return a sorted list of all canonical unit names known to the database.
std::vector<std::string> all_unit_names();

/// Return true if `unit` is a known unit (canonical or alias).
bool is_known_unit(const std::string& unit);

// ─── Unit categories ──────────────────────────────────────────────────────
// Used by the GUI and the Python bindings to group units in selectors.

struct UnitCategory {
    std::string              name;     // e.g. "Length"
    std::vector<std::string> units;    // canonical unit names in this category
};

std::vector<UnitCategory> unit_categories();

} // namespace unyts
