// unyts/binary_cache.cpp — full binary serialization (Phase 3).
//
// The cache stores:
//   1. All node names  (for schema-version / compatibility validation)
//   2. The BFS path-memory map  (pre-populates searches on warm starts)
//
// ConvFn objects are NOT serializable; populate_graph() is always re-run on
// startup.  The cache only avoids redundant BFS searches.
//
// File layout (little-endian, all integers fixed-width):
//   [CacheHeader]   (20 bytes)
//   [Node list]     node_count × (uint32 len + char[len])
//   [Path entries]  edge_count × (key_str + uint32 path_len + path_len × node_str)

#include "unyts/binary_cache.hpp"
#include "unyts/graph.hpp"

#include <cstring>
#include <fstream>
#include <stdexcept>

namespace unyts {

// ─── Low-level I/O helpers ────────────────────────────────────────────────────

static bool write_u32(std::ostream& os, uint32_t v) {
    os.write(reinterpret_cast<const char*>(&v), sizeof(v));
    return os.good();
}

static bool write_str(std::ostream& os, const std::string& s) {
    uint32_t len = static_cast<uint32_t>(s.size());
    if (!write_u32(os, len)) return false;
    os.write(s.data(), static_cast<std::streamsize>(len));
    return os.good();
}

static bool read_u32(std::istream& is, uint32_t& v) {
    return static_cast<bool>(is.read(reinterpret_cast<char*>(&v), sizeof(v)));
}

static bool read_str(std::istream& is, std::string& s,
                     uint32_t max_len = 4096) {
    uint32_t len = 0;
    if (!read_u32(is, len)) return false;
    if (len > max_len) return false;
    s.resize(len);
    return static_cast<bool>(
        is.read(s.data(), static_cast<std::streamsize>(len)));
}

// ─── save_cache ───────────────────────────────────────────────────────────────

void save_cache(const UDigraph& graph, const std::filesystem::path& path) {
    auto parent = path.parent_path();
    if (!parent.empty())
        std::filesystem::create_directories(parent);

    std::ofstream ofs(path, std::ios::binary | std::ios::trunc);
    if (!ofs)
        throw std::runtime_error(
            "unyts cache: cannot open '" + path.string() + "' for writing");

    auto  nodes  = graph.list_nodes();
    const auto& memmap = graph.memory_entries();

    CacheHeader hdr;
    hdr.node_count = static_cast<uint64_t>(nodes.size());
    hdr.edge_count = static_cast<uint64_t>(memmap.size());
    ofs.write(reinterpret_cast<const char*>(&hdr), sizeof(hdr));

    // Node names
    for (const auto& name : nodes)
        write_str(ofs, name);

    // Path-memory entries
    for (const auto& [key, path_vec] : memmap) {
        write_str(ofs, key);
        uint32_t plen = static_cast<uint32_t>(path_vec.size());
        write_u32(ofs, plen);
        for (const auto& node_name : path_vec)
            write_str(ofs, node_name);
    }

    if (!ofs)
        throw std::runtime_error(
            "unyts cache: write error on '" + path.string() + "'");
}

// ─── load_cache ───────────────────────────────────────────────────────────────

std::optional<UDigraph> load_cache(const std::filesystem::path& path) {
    if (!std::filesystem::exists(path)) return std::nullopt;

    std::ifstream ifs(path, std::ios::binary);
    if (!ifs) return std::nullopt;

    CacheHeader hdr;
    if (!ifs.read(reinterpret_cast<char*>(&hdr), sizeof(hdr)))
        return std::nullopt;

    if (hdr.magic != 0x554E5943U)           return std::nullopt;
    if (hdr.schema_version != UNYTS_CACHE_SCHEMA_VERSION) return std::nullopt;

    // Sanity limits
    if (hdr.node_count > 500'000)   return std::nullopt;
    if (hdr.edge_count > 50'000'000) return std::nullopt;

    UDigraph g;

    // Node names
    for (uint64_t i = 0; i < hdr.node_count; ++i) {
        std::string name;
        if (!read_str(ifs, name)) return std::nullopt;
        g.add_node(UNode{std::move(name)});
    }

    // Path-memory entries
    for (uint64_t i = 0; i < hdr.edge_count; ++i) {
        std::string key;
        if (!read_str(ifs, key)) return std::nullopt;

        uint32_t plen = 0;
        if (!read_u32(ifs, plen)) return std::nullopt;
        if (plen > 100'000) return std::nullopt;

        NodeNamePath path_vec;
        path_vec.reserve(plen);
        for (uint32_t j = 0; j < plen; ++j) {
            std::string node_name;
            if (!read_str(ifs, node_name)) return std::nullopt;
            path_vec.push_back(std::move(node_name));
        }
        g.set_memory(key, path_vec);
    }

    return g;
}

// ─── default_cache_path ───────────────────────────────────────────────────────

std::filesystem::path default_cache_path() {
    return std::filesystem::temp_directory_path() / "unyts_graph.cache";
}

// ─── cache_is_valid ───────────────────────────────────────────────────────────

bool cache_is_valid(const std::filesystem::path& path) {
    if (!std::filesystem::exists(path)) return false;
    std::ifstream ifs(path, std::ios::binary);
    if (!ifs) return false;
    CacheHeader hdr;
    if (!ifs.read(reinterpret_cast<char*>(&hdr), sizeof(hdr))) return false;
    return hdr.magic          == 0x554E5943U &&
           hdr.schema_version == UNYTS_CACHE_SCHEMA_VERSION;
}

} // namespace unyts

