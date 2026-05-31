// python/bindings.cpp — pybind11 bindings for the unyts C++ core.
//
// Module name: unyts_cpp_native  (matches unyts_cpp_native.cp314-win_amd64.pyd)
//
// The Python-side graceful fallback in converter.py is:
//   try:
//       from unyts_cpp_native import convert as _cpp_convert
//       _USE_CPP_ENGINE = True
//   except ImportError:
//       _USE_CPP_ENGINE = False
//
// Phase 1: exposes convert(), convertible(), conversion_factor(),
//          all_units(), is_known_unit(), and the graph/search classes.
// Phase 2: add combined-unit support, search memory API, fvf support.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>        // vector / optional ↔ Python list / None
#include <pybind11/functional.h> // std::function support
#include <optional>

#include "unyts/converter.hpp"
#include "unyts/database.hpp"
#include "unyts/graph.hpp"
#include "unyts/aliases.hpp"
#include "unyts/parser.hpp"

namespace py = pybind11;
using namespace unyts;

// ─────────────────────────────────────────────────────────────────────────────
// Helper: convert result → Python (value, bool) or None on failure
// ─────────────────────────────────────────────────────────────────────────────

static py::object py_convert(double value,
                              const std::string& from_unit,
                              const std::string& to_unit) {
    auto result = convert(value, from_unit, to_unit);
    if (!result) return py::none();
    return py::cast(result->value);
}

// ─────────────────────────────────────────────────────────────────────────────
PYBIND11_MODULE(unyts_cpp_native, m) {
    m.doc() = "unyts C++ core engine — unit conversion graph and search algorithms";

    // ── Version / build info ──────────────────────────────────────────────────
    m.attr("__version__") = "0.1.0";
    m.attr("CACHE_SCHEMA_VERSION") = UNYTS_CACHE_SCHEMA_VERSION;

    // ── Top-level conversion API ──────────────────────────────────────────────

    m.def("convert",
          &py_convert,
          py::arg("value"), py::arg("from_unit"), py::arg("to_unit"),
          R"(Convert a numeric value between two units.

Returns the converted float, or None if no conversion path exists.

Parameters
----------
value : float
    The numeric value to convert.
from_unit : str
    Source unit name (canonical or alias).
to_unit : str
    Target unit name (canonical or alias).
)");

    m.def("convertible",
          &convertible,
          py::arg("from_unit"), py::arg("to_unit"),
          "Return True when a conversion path between the two units exists.");

    m.def("conversion_factor",
          [](const std::string& from_unit, const std::string& to_unit) -> py::object {
              auto f = conversion_factor(from_unit, to_unit);
              return f ? py::cast(*f) : py::none();
          },
          py::arg("from_unit"), py::arg("to_unit"),
          "Return the numeric factor to convert 1 <from_unit> → <to_unit>, or None.");

    m.def("convertible_to",
          &convertible_to,
          py::arg("from_unit"),
          "Return a list of all unit names that from_unit can be converted to.");

    // ── Unit registry ─────────────────────────────────────────────────────────

    m.def("all_units",
          &all_unit_names,
          "Return a sorted list of all canonical unit names.");

    m.def("is_known_unit",
          &is_known_unit,
          py::arg("unit"),
          "Return True if the unit string is a known canonical name or alias.");

    m.def("unit_categories",
          []() {
              py::dict result;
              for (const auto& cat : unit_categories()) {
                  result[py::str(cat.name)] = py::cast(cat.units);
              }
              return result;
          },
          "Return a dict mapping category names to lists of unit names.");

    // ── Timeout control ───────────────────────────────────────────────────────

    m.def("set_timeout",
          &set_search_timeout_ms,
          py::arg("ms"),
          "Set the search timeout in milliseconds (default 5000).");

    m.def("get_timeout",
          &get_search_timeout_ms,
          "Get the current search timeout in milliseconds.");

    // ── Parser ────────────────────────────────────────────────────────────────

    m.def("is_compound_unit",
          &is_compound,
          py::arg("unit_str"),
          "Return True if the unit string contains *, /, or ^ operators.");

    m.def("normalize_unit",
          &normalize_unit,
          py::arg("unit"),
          "Resolve a unit alias to its canonical name, or return as-is if unknown.");

    // UnitToken — result of parse_unit
    py::class_<UnitToken>(m, "UnitToken")
        .def_readonly("name",     &UnitToken::name)
        .def_readonly("exponent", &UnitToken::exponent)
        .def("__repr__", [](const UnitToken& t) {
            return t.name + "^" + std::to_string(t.exponent);
        });

    m.def("parse_unit",
          &parse_unit,
          py::arg("unit_str"),
          R"(Parse a compound unit string into a list of UnitToken objects.

Examples:
  parse_unit("m/s")      -> [UnitToken("m",+1), UnitToken("s",-1)]
  parse_unit("kg*m/s^2") -> [UnitToken("kg",+1), UnitToken("m",+1), UnitToken("s",-2)]
Returns an empty list when the expression cannot be parsed.
)");

    // ── Low-level graph class (for debugging / advanced use) ──────────────────

    py::class_<UNode>(m, "UNode")
        .def(py::init<std::string>(), py::arg("name"))
        .def_readonly("name", &UNode::name)
        .def("get_name", &UNode::get_name)
        .def("__repr__", &UNode::str)
        .def("__eq__",   &UNode::operator==)
        .def("__hash__", [](const UNode& n) {
            return std::hash<std::string>{}(n.name);
        });

    py::class_<UDigraph>(m, "UDigraph")
        .def(py::init<>())
        .def("add_node",    [](UDigraph& g, const std::string& name) {
                                g.add_node(UNode{name}); },
             py::arg("name"))
        .def("has_node",    [](const UDigraph& g, const std::string& name) {
                                return g.has_node(name); },
             py::arg("name"))
        .def("list_nodes",  &UDigraph::list_nodes)
        .def("node_count",  &UDigraph::node_count)
        .def("memory_size", &UDigraph::memory_size)
        .def("clean_memory",&UDigraph::clean_memory)
        .def_readwrite("fvf", &UDigraph::fvf)
        .def_readwrite("recursion_limit", &UDigraph::recursion_limit)
        .def("__repr__",    &UDigraph::str);

    // ── Global graph access ───────────────────────────────────────────────────

    m.def("global_graph",
          []() -> UDigraph& { return global_graph(); },
          py::return_value_policy::reference,
          "Return the global singleton conversion graph.");
}
