#pragma once
// unyts/binary_cache.hpp — binary serialization of the conversion graph.
//
// Saves/loads a fully-populated UDigraph to a platform-independent binary
// format so that startup time is reduced on subsequent runs.
//
// Cache schema versioning is controlled by the compile-time constant
// UNYTS_CACHE_SCHEMA_VERSION (set in CMakeLists.txt).
//
// Phase 2: full implementation.
// Phase 1: declarations only.

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>

namespace unyts {

class UDigraph;

// ─── Cache file header ────────────────────────────────────────────────────────
struct CacheHeader {
    uint32_t magic          = 0x554E5943; // 'UNYC'
    uint32_t schema_version = UNYTS_CACHE_SCHEMA_VERSION;
    uint64_t node_count     = 0;
    uint64_t edge_count     = 0;
};

// ─── Cache operations ─────────────────────────────────────────────────────────

/// Attempt to load a cached graph from path.
/// Returns nullopt if the file does not exist, is corrupt, or has a schema
/// version mismatch.
std::optional<UDigraph> load_cache(const std::filesystem::path& path);

/// Persist graph to path, overwriting any existing file.
/// Throws std::runtime_error on I/O failure.
void save_cache(const UDigraph& graph, const std::filesystem::path& path);

/// Return the default cache file location (next to the shared library).
std::filesystem::path default_cache_path();

/// Return true if the cache at path is valid and schema-compatible.
bool cache_is_valid(const std::filesystem::path& path);

} // namespace unyts
