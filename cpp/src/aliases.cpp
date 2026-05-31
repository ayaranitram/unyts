// unyts/aliases.cpp — stub implementation (Phase 1).
// Full unit alias data will be populated here in Phase 2.

#include "unyts/aliases.hpp"
#include <stdexcept>

namespace unyts {

// ─── AliasRegistry ───────────────────────────────────────────────────────────

void AliasRegistry::add_synonym(const std::string& alias,
                                 const std::string& canonical) {
    map_[alias] = AliasEntry{canonical, 1.0, true};
}

void AliasRegistry::add_scaled(const std::string& alias,
                                const std::string& canonical,
                                double factor) {
    map_[alias] = AliasEntry{canonical, factor, true};
}

std::optional<std::string> AliasRegistry::canonical(const std::string& alias) const {
    auto it = map_.find(alias);
    if (it == map_.end()) return std::nullopt;
    return it->second.canonical;
}

const AliasEntry* AliasRegistry::lookup(const std::string& alias) const {
    auto it = map_.find(alias);
    return (it == map_.end()) ? nullptr : &it->second;
}

std::vector<std::string> AliasRegistry::all_aliases() const {
    std::vector<std::string> result;
    result.reserve(map_.size());
    for (const auto& kv : map_) result.push_back(kv.first);
    return result;
}

bool AliasRegistry::is_known(const std::string& name) const {
    return map_.count(name) > 0;
}

// ─── Global registry ─────────────────────────────────────────────────────────

AliasRegistry& global_alias_registry() {
    static AliasRegistry instance;
    return instance;
}

// ─── normalize_unit ──────────────────────────────────────────────────────────

std::string normalize_unit(const std::string& name) {
    auto canonical = global_alias_registry().canonical(name);
    return canonical.value_or(name);
}

} // namespace unyts
