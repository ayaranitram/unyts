#pragma once
// unyts/types.hpp — fundamental type aliases shared across the engine.

#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace unyts {

/// Conversion function: takes a double value and returns the converted value.
using ConvFn = std::function<double(double)>;

/// A flat list of node names representing a path through the conversion graph.
/// Filled in by the search algorithms; applied by apply_path().
using NodeNamePath = std::vector<std::string>;

} // namespace unyts
