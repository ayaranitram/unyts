#pragma once
// unyts/graph.hpp — directed graph, node/edge types, and search algorithms.
//
// This is the central header for the C++ unyts engine.  It defines:
//   UNode      — a named node in the unit conversion graph
//   Conversion — a directed edge with an associated conversion function
//   UDigraph   — the directed graph itself, with BFS/DFS search methods
//
// Search algorithms (BFS, DFS, lean_BFS, hybrid_BFS) are free functions
// declared at the bottom of this header and implemented in graph.cpp.

#include <chrono>
#include <functional>
#include <optional>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "unyts/types.hpp"

namespace unyts {

// ─── UNode ────────────────────────────────────────────────────────────────────
// A lightweight node identified entirely by its name string.
// Equality and hashing are name-based so that nodes rebuilt across sessions
// compare equal — this mirrors the Python UNode.__eq__/__hash__ design.

struct UNode {
    std::string name;

    UNode() = default;
    explicit UNode(std::string n) noexcept : name(std::move(n)) {}

    const std::string& get_name() const noexcept { return name; }
    std::string        str()      const           { return name; }

    bool operator==(const UNode& o) const noexcept { return name == o.name; }
    bool operator!=(const UNode& o) const noexcept { return name != o.name; }
};

} // namespace unyts

// std::hash specialisation — must live in namespace std before UDigraph uses it
namespace std {
    template<> struct hash<unyts::UNode> {
        size_t operator()(const unyts::UNode& n) const noexcept {
            return std::hash<std::string>{}(n.name);
        }
    };
} // namespace std

namespace unyts {

// ─── Conversion ───────────────────────────────────────────────────────────────
// A directed edge between two UNodes plus a conversion function.
//   rev=true  → the edge was generated as a reverse of another edge;
//               get_convert() returns  x => x / conv(1)  (mirrors Python)
//   alias=true → the edge represents an alias relationship

struct Conversion {
    UNode  src;
    UNode  dest;
    ConvFn conv;
    bool   rev   = false;
    bool   alias = false;

    Conversion() = default;
    Conversion(UNode s, UNode d, ConvFn fn,
               bool reverse = false, bool is_alias = false)
        : src(std::move(s)), dest(std::move(d)), conv(std::move(fn)),
          rev(reverse), alias(is_alias) {}

    const UNode& get_source()      const noexcept { return src; }
    const UNode& get_destination() const noexcept { return dest; }

    // Mirrors Python Conversion.get_convert():
    //   if rev, return a wrapper that computes  x / conv(1)
    //   otherwise return conv directly
    ConvFn get_convert() const;

    double convert_value(double value)   const { return conv(value); }
    double reverse_value(double value)   const { return value / conv(1.0); }

    std::string str() const { return src.name + "->" + dest.name; }
};

// ─── Internal edge storage ────────────────────────────────────────────────────
// dest + the *effective* conversion function (get_convert() already applied)

struct EdgeEntry {
    UNode  dest;
    ConvFn fn;
};

// ─── UDigraph ─────────────────────────────────────────────────────────────────
// Directed graph mapping each UNode to its list of outgoing EdgeEntries.
//
// The Python UDigraph.edges maps  node → ([dest_nodes], [conv_functions])
// using parallel lists.  Here we merge them into a single vector<EdgeEntry>
// per source node, which is cleaner and cache-friendlier.

class UDigraph {
public:
    UDigraph() = default;

    // ── Graph building ────────────────────────────────────────────────────────
    // Silently ignores duplicate nodes (mirrors Python behaviour).
    void add_node(const UNode& node);

    // Requires both src and dest to already be present; throws std::invalid_argument
    // if either is missing.  Duplicate edges are silently ignored.
    void add_edge(const Conversion& edge);

    // ── Graph queries ─────────────────────────────────────────────────────────
    bool         has_node(const UNode& node)       const;
    bool         has_node(const std::string& name) const;

    // Returns pointer to the stored node, or nullptr if absent.
    const UNode* get_node(const std::string& name) const;

    std::vector<std::string> list_nodes() const;
    size_t node_count() const noexcept { return nodes_.size(); }

    // Returns all outgoing edges for a node.  Returns an empty vector if the
    // node is not in the graph (rather than throwing) — mirrors Python children_of.
    const std::vector<EdgeEntry>& children_of(const UNode& node) const;

    // Apply the stored conversion function from src → dest.
    // Throws std::out_of_range if the edge does not exist.
    double convert(double value,
                   const UNode& src, const UNode& dest) const;
    double convert(double value,
                   const std::string& src, const std::string& dest) const;

    // Returns the conversion function for the src→dest edge.
    ConvFn conversion(const UNode& src, const UNode& dest) const;

    // ── Search memory cache ───────────────────────────────────────────────────
    // Stores previously found paths so they don't need to be re-searched.
    // Key format: "from_unit|to_unit"
    bool has_memory(const std::string& key) const;
    void set_memory(const std::string& key, const NodeNamePath& path);
    const NodeNamePath* get_memory(const std::string& key) const; // nullptr = miss
    void   clean_memory();
    size_t memory_size() const noexcept { return memory_.size(); }

    // Read-only access to the full memory map (used by binary_cache.cpp).
    const std::unordered_map<std::string, NodeNamePath>& memory_entries() const noexcept {
        return memory_;
    }

    // ── Miscellaneous state ───────────────────────────────────────────────────
    double fvf            = -1.0; // Formation Volume Factor; -1 = unset
    int    recursion_limit = 5;

    std::string str() const;

private:
    std::unordered_map<std::string, UNode>                  nodes_;
    std::unordered_map<std::string, std::vector<EdgeEntry>> edges_;
    std::unordered_map<std::string, NodeNamePath>           memory_;

    static const std::vector<EdgeEntry> empty_edges_;
};

// ─── Search path type ─────────────────────────────────────────────────────────
// A path is a sequence of UNodes from the start node to the end node (inclusive).
using Path = std::vector<UNode>;

// ─── Clock / deadline helpers ─────────────────────────────────────────────────
using Clock     = std::chrono::steady_clock;
using TimePoint = Clock::time_point;

inline TimePoint make_deadline(int timeout_ms) {
    return Clock::now() + std::chrono::milliseconds(timeout_ms);
}
inline TimePoint no_deadline() {
    return Clock::time_point::max();
}

// ─── Search algorithms ────────────────────────────────────────────────────────

/// Breadth-first search.  Returns the shortest path from start to end,
/// or std::nullopt if unreachable or if the deadline is exceeded.
std::optional<Path> BFS(const UDigraph& g,
                        const UNode& start, const UNode& end,
                        TimePoint deadline = no_deadline(),
                        bool verbose = false);

/// Depth-first search with optional branch pruning.
/// branch_depth: max hops to look ahead when deciding whether a branch can
/// reach end (mirrors Python DFS's branch_depth parameter).
/// Setting branch_depth to 0 disables pruning.
std::optional<Path> DFS(const UDigraph& g,
                        const UNode& start, const UNode& end,
                        TimePoint deadline = no_deadline(),
                        bool verbose = false,
                        int branch_depth = 0);

/// Lean BFS: builds a trimmed subgraph from the intersection of nodes
/// reachable from start and nodes that can reach end, then runs BFS on it.
/// Typically 10–100× faster than plain BFS on large graphs.
std::optional<Path> lean_BFS(const UDigraph& g,
                             const UNode& start, const UNode& end,
                             TimePoint deadline = no_deadline(),
                             bool verbose = false,
                             int max_generations = 25);

/// Hybrid BFS: launches BFS and lean_BFS in separate threads and returns
/// whichever result arrives first.
std::optional<Path> hybrid_BFS(const UDigraph& g,
                               const UNode& start, const UNode& end,
                               TimePoint deadline = no_deadline(),
                               bool verbose = false,
                               int max_generations = 25);

// ─── Path utilities ───────────────────────────────────────────────────────────

/// Apply a node-sequence path to a value by chaining the graph's edge functions.
double apply_path(const UDigraph& g, const Path& path, double value);

/// Format a path as "nodeA -> nodeB -> nodeC".
std::string path_to_string(const Path& path);

/// Return all node names reachable from start_name within max_depth hops.
std::unordered_set<std::string> get_descendants(
    const UDigraph& g,
    const std::string& start_name,
    int max_depth);

} // namespace unyts
