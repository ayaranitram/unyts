# Plan: C++ Port + Windows Desktop Application

> **This plan also defines the shared C++ core engine** that is the foundation for the iOS and Android apps.
> See [PLAN_IOS.md](PLAN_IOS.md) and [PLAN_ANDROID.md](PLAN_ANDROID.md) for the mobile ports.

---

## Progress Log

| Phase | Status | Date | Notes |
|-------|--------|------|-------|
| 0 — Environment Setup | ✅ Done | 2026-05-30 | CMake 3.15 + MSVC 19.50 (VS 2026) + pybind11 from .venv |
| 1 — Core Graph Engine | ✅ Done | 2026-05-30 | All files compile and smoke-tests pass |
| 2 — Unit Registry + Conversions | ✅ Done | 2026-05-30 | 1413 units; 23/23 tests pass; bugs fixed (inverted time edges, km alias) |
| 3 — Binary Cache | ✅ Done | 2026-05-30 | Schema-versioned binary cache with load/save |
| 4 — Compound Unit Parser | ✅ Done | 2026-05-30 | Full tokenizer for `m/s`, `kg*m/s^2`, `ft^3/day` etc. |
| 4b — Parity Fixes (CI + aliases) | ✅ Done | 2026-05-31 | 48.4% → **100%** parity (2256/2256), 0 wrong values — 6 fix rounds |
| 5 — Qt Windows GUI | ✅ Done | 2026-05-31 | Qt 6.10.2/MinGW; unit autocomplete, bidirectional conversion, path marquee, menus; 325×235 px (matches Python GUI), `unyts_icon.ico` as EXE + window icon |
| 6 — C API Surface | ✅ Done | 2026-05-31 | `unyts_capi.dll` (MSVC); 25/25 smoke tests pass; stable C ABI for iOS/Android/FFI |
| 7 — Polish + Testing | ⬜ Not started | — | C++ compound-unit gradient fix (`psig/ft → kPa/m`) already in core; parity suite 2256/2256; benchmark + installer next |

### Phase 0 — Completed

- Build system: `cpp/CMakeLists.txt` with NMake + MSVC, C++17
- Toolchain: MSVC 19.50 (`cl.exe`), CMake 3.15, VS 2026 Community
- pybind11 sourced from `.venv/Lib/site-packages/pybind11` (no separate install needed)
- Build dir: `cpp/build_new/`  
- Build command: `cmake .. -G "NMake Makefiles" -DCMAKE_BUILD_TYPE=Release -DPYBIND11_DIR="D:/git/unyts/.venv/Lib/site-packages/pybind11"`

### Phase 1 — Completed

Files created:

| File | Purpose |
|------|---------|
| `cpp/include/unyts/types.hpp` | `ConvFn`, `NodeNamePath` type aliases |
| `cpp/include/unyts/graph.hpp` | `UNode`, `Conversion`, `UDigraph`, BFS/DFS declarations |
| `cpp/src/graph.cpp` | Full `BFS`, `DFS`, `lean_BFS`, `hybrid_BFS`, `apply_path`, `get_descendants` |
| `cpp/include/unyts/aliases.hpp` | `AliasRegistry` declarations |
| `cpp/include/unyts/binary_cache.hpp` | Cache load/save declarations |
| `cpp/include/unyts/database.hpp` | `populate_graph`, `global_graph` declarations |
| `cpp/include/unyts/converter.hpp` | `convert`, `convertible`, `conversion_factor` declarations |
| `cpp/include/unyts/parser.hpp` | `UnitToken`, `parse_unit` declarations |
| `cpp/src/aliases.cpp` | `AliasRegistry` implementation |
| `cpp/src/binary_cache.cpp` | Stub (Phase 2) |
| `cpp/src/database.cpp` | Phase 1 length units + aliases (stub, replaced in Phase 2) |
| `cpp/src/converter.cpp` | `convert`/`convertible` via `hybrid_BFS` |
| `cpp/src/parser.cpp` | Stub (Phase 2) |
| `cpp/python/bindings.cpp` | pybind11 module `unyts_cpp_native` |

Smoke-test results (Phase 1 stub data — 9 length units):

```
1 m → km:  0.001 ✓      1 km → m:   1000.0 ✓
1 ft → in: 12.0  ✓      1 mi → km:  1.609344 ✓
12 in → yd: 0.333... ✓  3 ft → yd:  1.0 ✓
1 metre → km: 0.001 ✓   1 kilometer → m: 1000.0 ✓
convertible(m, ft): True   convertible(m, kg): False ✓
```

### Phase 2 — Completed ✅

Replaced the Phase 1 stub with the full unit catalogue ported from the Python sources.
Fixed two post-completion bugs: inverted time-chain edges and disconnected `kilometer` node.

| File | Purpose |
|------|---------|
| `cpp/include/unyts/conversions.hpp` | Declarations for ~130 conversion functions + physical constants |
| `cpp/src/conversions.cpp` | All conversion functions ported from `def_conversions.py` |
| `cpp/src/database.cpp` | **Full rewrite** — 20 unit categories, SI/OGF/DATA prefix expansion, FVF lambda |

Smoke-test results (1413 known units, 23 conversion tests):

```
km→m: 1000.0 ✓    ft→m: 0.3048 ✓      mile→km: 1.609344 ✓
C→F: 212.0 ✓      Celsius→Kelvin: 273.15 ✓  bara→psia: 14.5038 ✓
minute→second: 60 ✓  day→hour: 24 ✓   year→day: 365.25 ✓
millisecond→s: 0.001 ✓  s→millisecond: 1000 ✓  ns→s: 1e-9 ✓
kg→lb: 2.2046 ✓   stb→gallonUS: 42 ✓  scf→sm3: 0.028317 ✓
kWh→J: 3600000 ✓  Darcy→mD: 1000 ✓    gal→litre: 3.7854 ✓
W→hp: 0.001341 ✓  cP→Pa*s: 0.001 ✓    kJ→BTU: 0.94787 ✓
```

### Phase 3 — Completed ✅

| File | Purpose |
|------|---------|
| `cpp/src/binary_cache.cpp` | Schema-versioned binary serialization of `UDigraph` |

### Phase 4 — Completed ✅

| File | Purpose |
|------|---------|
| `cpp/src/parser.cpp` | Full compound-unit tokenizer: `m/s`, `kg*m/s^2`, `ft^3/day` |

### Phase 4b — Parity Fixes ✅  (2026-05-31)

Four gap-closing fixes to maximise coverage against the Excel reference dataset (2256 rows):

**Fix 1 — Case-insensitive lookup (`converter.cpp`)**  
`resolve_name()` now tries 3 steps before falling back:
1. Exact alias lookup (original behaviour)
2. Lowercase alias lookup — only when the registry maps to a *different* name (prevents `MSM3` → `msm3` milli-prefix collision)
3. Full case-insensitive node scan — only when the match is unique (prevents prefix-case ambiguity)

**Fix 2 — Correct cwt / t aliases (`database.cpp`)**  
- `cwt` → `long hundredweight` (112 lb UK), not `short hundredweight` (100 lb US)
- `t` → `long ton` (2240 lb UK), not `metric ton`; added `tonne`/`mt`/`MT` → `metric ton`

**Fix 3 — Plural & short-form time aliases (`database.cpp`)**  
Added: `seconds`, `minutes`, `hours`, `days`, `weeks`, `months`, `years`, `decades`, `centuries`,
`nanoseconds`, `milliseconds`, `sec`, `min`, `hr`, `w`/`wk`/`wks`, `mo`, `yr`/`yrs`.  
Also Spanish: `día`/`días`, `año`/`años`, `mes`/`meses`.

**Fix 4 — Miscellaneous missing aliases (`database.cpp`)**  
- Volume: `decilitre`/`deciliter`/`dL`, `centilitre`/`centiliter`/`cL`, `stbl`, `oil barrel`, `cc`/`mL`, `standard cubic centimeter`
- Pressure: `abs bar`, `bar absolute`, `absolute pound/square inch`, `gauge psi`, `psi gauge`, `gauge bar`, `bar gauge`, `absolute bara`
- Temperature: `degrees F`/`degrees Fahrenheit`, `degrees K`/`degrees Kelvin`, `degrees R`/`degrees Rankine`
- Area: `sqmeter`, `sq m`, `m*m`, `m3/m`, `sqkm`, `sq km`, `sqmile`, `sq mi`, `mi*mi`, `sqft`, `sq ft`, `ft*ft`, `ft3/ft`, `sqin`, `sq in`, `sqyd`, `sq yd`, `sqrd`, `sq rd`, `sqcm`, `sq cm`
- Energy: `joule`, `joules`, `calories`
- Weight: `milligrams`, `grams`, `kilograms`, `kgs`, `mgs`, `ounces`, `pounds`, `lbs`, `tons`, `kgm`
- Length: `meters`, `metre`, `metres`, `feet`, `inches`, `in`, `yards`, `miles`, `kilometers`, `kilometres`, etc.
- Viscosity: `cps`

**Fix 5 — Spanish uppercase, gallon/cubic variants, pressure names, energy/viscosity (`database.cpp`)**
Added: Spanish uppercase forms (`DÍAS`, `AÑOS`), `gallonUS`/`gallonUS1`/`gallonUK` variants, `cubic feet`/`cubic yards`/`cubic miles`, pressure names (`pounds per square inch`, `kilopascal`, etc.), OGF case aliases (`OGF`/`SCFSTB`/`MSCFSTB`), productivity dash-notation (`stb/day-psi`, `sm3/day-kpa`), energy/viscosity compounds (`kJ/mol`, `cal/mol`, `BTU/mol`, `Pa*s`/`mPa*s`).  
Coverage: **84.9% (1916/2256), 0 wrong values**

**Fix 6 — Comprehensive alias and physics expansion (`database.cpp`)**  
Added: time/area/volume compound notation, OGF uppercase CI bypasses (`MSM3`, `KSM3`), fluid ounce cross-category `fn_pair`, gill/pint/quart/litre plurals, cubic-volume hyphenated/plural forms, standard/reservoir volume abbreviations, barrel variants, pressure gradient chain (`lb/ft³ ↔ psia/ft ↔ kPa/m ↔ bara/m`), density connections (`SgO/SgW ↔ g/cc`, `SgG ↔ kg/m³`), density ratio `lb/stb`, weight/mass aliases, Poise viscosity alias, `kWh`/`KWH`, productivity truncated-slash variants, UK fluid volume abbreviations, speed nodes (`ft/sec ↔ m/s`, `km/h ↔ km/day`), temperature gradient units (`F/ft ↔ C/m ↔ K/m ↔ C/km ↔ C/cm`, `F/ft ↔ F/in ↔ F/yd`), temperature rate-of-change units (`C/min ↔ C/hour ↔ C/day`, `C/min ↔ F/min ↔ F/s`).  
Coverage: **100% (2256/2256), 0 wrong values** ✅

**Final coverage results (Excel reference, 2256 test rows):**

| Milestone | Coverage | Wrong values |
|-----------|----------|------------|
| After Phase 4 (before fixes) | 48.4% (1092/2256) | many |
| After Fix 1 (CI lookup) | ~72% | reduced |
| After Fixes 1–4 (all aliases) | 78.4% (1769/2256) | **0** |
| After Fix 5 (gallon/cubic/pressure/energy) | 84.9% (1916/2256) | **0** |
| After Fix 6 (pressure gradient/density/gradients) | **100% (2256/2256)** | **0** |

### Phase 6 — Completed ✅  (2026-05-31)

| File | Purpose |
|------|---------|
| `cpp/include/unyts/unyts_capi.h` | Pure-C public API header (`extern "C"`, DLL import/export macros, return codes) |
| `cpp/capi/unyts_capi.cpp` | Implementation: `UnytsContext` wraps per-context FVF/timeout on top of global singleton graph |
| `cpp/capi/test_capi.c` | Plain-C smoke-test (25/25 pass, compiled with MSVC `cl.exe`) |

Functions exposed: `unyts_create/destroy`, `unyts_convert`, `unyts_convertible`, `unyts_conversion_factor`, `unyts_all_units`, `unyts_unit_count`, `unyts_is_known_unit`, `unyts_set/get_fvf`, `unyts_set/get_timeout_ms`, `unyts_version`.

Build produces `unyts_capi.dll` + `unyts_capi.lib` (MSVC).  The stable C ABI bridges the MSVC↔MinGW compiler gap and is the interface consumed by the Qt GUI, the iOS Obj-C++ wrapper, and the Android JNI layer.

**Smoke-test results (25/25):**

```
PASS  unyts_create() returns non-NULL        (1706 units registered)
PASS  'meter' / 'kg' is known; 'xyzzy' unknown
PASS  meter→foot / kg→lb convertible; meter→kg not
PASS  1 km → m = 1000     PASS  1 m → ft = 3.28084
PASS  212 F → C = 100     PASS  1 bara → psia ≈ 14.5038
PASS  1 stb → m3 ≈ 0.158987
PASS  UNYTS_ERR_NO_PATH / UNYTS_ERR_BADARG correctly returned
PASS  conversion_factor kg→lb ≈ 2.2046
PASS  set/get FVF and timeout
PASS  all_units overflow / large-buffer / null-terminate
PASS  unyts_destroy(NULL) no-crash
```

### Phase 5 — Completed ✅  (2026-05-31)

| File | Purpose |
|------|---------|
| `cpp/gui_windows/CMakeLists.txt` | MinGW + Qt 6.10.2 build; re-compiles core as `unyts_core_mingw` to avoid MSVC/MinGW ABI mismatch |
| `cpp/gui_windows/main.cpp` | `QApplication` entry point |
| `cpp/gui_windows/MainWindow.h` | Window declaration |
| `cpp/gui_windows/MainWindow.cpp` | Full implementation |

**Features (parity with `gui.py`):**
- Title label, 3-column grid: `from unit / from value` + `to unit / to value`
- `QCompleter` with `QSortFilterProxyModel` for case-insensitive unit autocomplete (all 1706 units)
- **Convert** button + Enter key in any field triggers `_calculate`; Enter in to-value triggers reverse conversion
- **Repeat search** checkbox (clears cache for next call)
- Status label shows timing (ms/s)
- Conversion path row with marquee animation for long strings (hidden by default)
- Menu: **File** (load/save/clean memory, exit), **Options** (FVF, timeout, show path toggle), **Help** (docs, about)
- Fixed window size **325 × 235 px**, non-resizable — matches Python tkinter GUI on Windows
- Application icon (`unyts_icon.ico`) set as both the **EXE file icon** (Windows Explorer/taskbar, via `app.rc`) and the **window titlebar icon** (via Qt resource `resources.qrc` + `setWindowIcon`)

**New files:**

| File | Purpose |
|------|---------|
| `cpp/gui_windows/resources.qrc` | Qt resource file — embeds `unyts_icon.ico` for runtime use |
| `cpp/gui_windows/app.rc` | Windows resource file — sets EXE file icon |

**Build toolchain:** Qt 6.10.2 / MinGW 13.1.0 / CMake 3.30.5 (Qt-bundled)  
**Build dir:** `cpp/build_gui/`  
**Build command:**
```powershell
# MinGW must be in PATH — required for g++ to locate its runtime DLLs
$env:PATH = "C:\Qt\Tools\mingw1310_64\bin;" + $env:PATH
cmake --build cpp/build_gui
```
**Run command:**
```powershell
$env:PATH = "C:\Qt\6.10.2\mingw_64\bin;C:\Qt\Tools\mingw1310_64\bin;" + $env:PATH
.\cpp\build_gui\unyts_gui.exe
```

---

## 1. Overview

Port the unyts engine from Python to a native C++ library (`libunyts`) and build a Windows desktop application on top of it using the **Qt 6** framework.  The resulting C++ library is platform-agnostic and will be reused, without changes, by the iOS and Android builds.

### Goals
- Full feature-parity with the Python library (same unit catalogue, BFS/DFS, FVF, parameters, caching)
- Native Windows `.exe` with an equivalent GUI to `gui.py`
- A clean C API surface (`unyts_capi.h`) so any language can call the library via FFI
- A shared CMake build system that cross-compiles to Windows, iOS (arm64), and Android (arm64-v8a / x86_64)
- **pybind11 Python bindings** (`unyts_cpp` module) so the C++ engine can replace the pure-Python engine while keeping the existing Python API intact

---

## 2. Architecture

```
┌────────────────────────────────────────────────────┐
│            Qt 6 Windows Desktop Application        │
│            (Qt Widgets or Qt Quick / QML)          │
│                       gui/                         │
└──────────────────────┬─────────────────────────────┘
                       │ C++ API
┌──────────────────────▼─────────────────────────────┐
│                 unyts C++ Core Library              │
│                   (libunyts.lib / .dll)             │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  UDigraph   │  │ Registry │  │   Converter   │  │
│  │  UNode      │  │ (units/  │  │   convert()   │  │
│  │  Conversion │  │  dict)   │  │  convertible()│  │
│  └─────────────┘  └──────────┘  └───────────────┘  │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  BFS / DFS  │  │ Params / │  │    Cache /    │  │
│  │  hybrid_BFS │  │ Settings │  │  Persistence  │  │
│  └─────────────┘  └──────────┘  └───────────────┘  │
└────────────────────────────────────────────────────┘
                       │ C API (unyts_capi.h)
         ┌─────────────┼──────────────┐
    iOS Bridge     Android JNI    pybind11
 (Obj-C++ wrapper) (JNI wrapper) (unyts_cpp.pyd)
                                  ↑ drop-in replacement
                                    for pure-Python unyts
```

---

## 3. Python → C++ Module Mapping

| Python module | C++ equivalent | Priority |
|---|---|---|
| `network.py` | `unyts/core/graph.h/.cpp` | **P0 – blocker** |
| `searches.py` | `unyts/core/search.h/.cpp` | **P0 – blocker** |
| `dictionaries.py` | `unyts/core/registry.h/.cpp` | **P0 – blocker** |
| `units/def_conversions.py` | `unyts/core/conversions.h/.cpp` | **P0 – blocker** |
| `units/def_prefixes.py` | `unyts/core/prefixes.h/.cpp` | P1 |
| `units/*.py` (all categories) | `unyts/core/units/*.cpp` | P1 |
| `converter.py` | `unyts/core/converter.h/.cpp` | P1 |
| `parameters.py` | `unyts/core/parameters.h/.cpp` | P1 |
| `operations.py` | `unyts/core/operations.h/.cpp` | P2 |
| `unit_class.py` | `unyts/core/unit.h/.cpp` | P2 |
| `database.py` | `unyts/core/database.h/.cpp` | P2 |
| `searches.py` (timeout/threading) | `unyts/core/timer.h/.cpp` | P2 |
| `gui.py` | `unyts/gui/mainwindow.h/.cpp` (Qt) | P3 |
| C API surface | `unyts/capi/unyts_capi.h/.cpp` | P3 |
| Python bindings | `unyts/bindings_python/bindings.cpp` (pybind11) | P4 |

---

## 4. Technology Stack

| Component | Choice | Rationale |
|---|---|---|
| Language | C++17 | Widely supported on all target platforms; `std::string_view`, structured bindings, `if constexpr` reduce boilerplate |
| Build system | CMake 3.21+ | Single source of truth for Windows, iOS, Android; Hunter/vcpkg for dependencies |
| Windows GUI | Qt 6.7 (Widgets) | Mature, LGPL, excellent Windows support; Qt Creator IDE bonus |
| JSON/serialization | nlohmann/json (header-only) | Cache persistence replacing Python's cloudpickle/pickle |
| Unit tests | Catch2 or GoogleTest | Mirrors the existing pytest suite |
| Python bindings | pybind11 (header-only, MIT) | Exposes C++ API as a native Python extension module |
| Packaging | WiX Toolset or NSIS (via CPack) | Windows installer |

---

## 5. Component Details

### 5.1 Graph Engine (`graph.h/.cpp`)

Port of `network.py` (~284 lines).

```cpp
// unyts/core/graph.h (sketch)
#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>

namespace unyts {

using ConvFn = std::function<double(double)>;

struct UNode {
    std::string name;
    bool operator==(const UNode& o) const { return name == o.name; }
};

struct Conversion {
    UNode from;
    UNode to;
    ConvFn fn;
};

class UDigraph {
public:
    void add_node(const UNode& node);
    void add_edge(const Conversion& conv);
    bool has_node(const std::string& name) const;
    const UNode* get_node(const std::string& name) const;
    const std::vector<Conversion>& children_of(const UNode& node) const;
    // cache access
    bool has_memory(const std::string& key) const;
    double get_memory(const std::string& key) const;
    void set_memory(const std::string& key, double value);
private:
    std::unordered_map<std::string, UNode> nodes_;
    std::unordered_map<std::string, std::vector<Conversion>> edges_;
    std::unordered_map<std::string, double> memory_;
};

} // namespace unyts
```

Key decisions:
- `ConvFn` is `std::function<double(double)>`; all conversion lambdas from Python map directly
- Node equality and hashing based on `name` string (mirrors Python `UNode.__eq__` / `__hash__`)
- `children_of()` returns const reference to avoid copies

### 5.2 Search Algorithms (`search.h/.cpp`)

Port of `searches.py` (~268 lines).  All three algorithms (BFS, lean_BFS, DFS, hybrid_BFS) should be ported.

```cpp
// unyts/core/search.h (sketch)
#pragma once
#include "graph.h"
#include <optional>
#include <vector>
#include <chrono>

namespace unyts {

using Path = std::vector<Conversion>;
using TimePoint = std::chrono::steady_clock::time_point;

std::optional<Path> BFS(const UDigraph& g,
                        const UNode& start, const UNode& end,
                        TimePoint deadline);

std::optional<Path> DFS(const UDigraph& g,
                        const UNode& start, const UNode& end,
                        TimePoint deadline, int max_depth = 5);

std::optional<Path> hybrid_BFS(const UDigraph& g,
                               const UNode& start, const UNode& end,
                               TimePoint deadline);
} // namespace unyts
```

Notes:
- Python's `unyts_parameters_.is_intime()` becomes a `deadline` parameter (avoids globals)
- `std::optional<Path>` replaces Python's `Empty` sentinel

### 5.3 Unit Registry (`registry.h/.cpp`)

Port of `dictionaries.py` (~774 lines) + all `units/*.py` files.

The registry:
- Maps canonical unit names → set of aliases
- Maps (from_unit, to_unit) pairs → `ConvFn`
- Populates a `UDigraph` on startup

```cpp
namespace unyts {

struct UnitEntry {
    std::string canonical;           // e.g. "meter"
    std::vector<std::string> aliases; // e.g. {"m", "metre", "meters", ...}
    std::string dimension;           // e.g. "Length"
};

class Registry {
public:
    static Registry& instance();          // singleton
    void build(UDigraph& graph) const;    // populate graph from registry
    bool is_valid_unit(std::string_view s) const;
    std::vector<std::string> all_units() const;
    std::string canonical(std::string_view alias) const;
    std::string dimension_of(std::string_view unit) const;
private:
    Registry();
    std::vector<UnitEntry> units_;
    std::unordered_map<std::string, size_t> alias_map_; // alias → index in units_
};

} // namespace unyts
```

**This is the most labour-intensive component** because every Python lambda in `def_conversions.py` (~200 functions across 989 lines) must be transcribed to a C++ `ConvFn`.  However, the work is mechanical — each Python function body maps 1:1 to a C++ lambda or named function.

### 5.4 Converter (`converter.h/.cpp`)

Port of `converter.py` (~997 lines).

```cpp
namespace unyts {

struct ConvertResult {
    double value;
    std::string path_str;    // human-readable conversion path
    bool success;
    std::string error_msg;
};

ConvertResult convert(double value,
                      std::string_view from_unit,
                      std::string_view to_unit,
                      const Parameters& params);

bool convertible(std::string_view from_unit,
                 std::string_view to_unit,
                 const Parameters& params);

} // namespace unyts
```

### 5.5 Parameters (`parameters.h/.cpp`)

Port of `parameters.py` (~521 lines).

```cpp
namespace unyts {

struct Parameters {
    bool parallel = false;
    std::string algorithm = "BFS";  // "BFS" | "DFS" | "hybrid"
    int timeout_ms = 3000;
    double fvf = 1.0;
    bool print_path = false;
    bool verbose = false;
    bool raise_error = false;
    bool cache = true;
    // ...
    void load(const std::filesystem::path& ini_path);
    void save(const std::filesystem::path& ini_path) const;
};

} // namespace unyts
```

INI file parsing: use a simple custom parser or the `inih` library (header-only, MIT).

### 5.6 Persistence / Cache (`database.h/.cpp`)

Port of `database.py` (~1094 lines).

- Replace Python `cloudpickle`/`pickle` with `nlohmann/json` for the search-path memory cache
- Graph structure itself is rebuilt at startup from the in-code registry (fast, no need to persist the graph)
- Cache file location: `%APPDATA%\unyts\` on Windows, `~/.config/unyts/` on Linux/macOS, app-sandboxed directory on iOS/Android

### 5.7 C API Surface (`unyts_capi.h`)

A thin pure-C wrapper that allows the library to be called from any language without C++ name-mangling issues.  This is the interface consumed by the iOS Objective-C++ bridge and the Android JNI layer.

```c
// unyts_capi.h
#ifdef __cplusplus
extern "C" {
#endif

typedef struct UnytsContext UnytsContext;

UnytsContext* unyts_create(void);
void          unyts_destroy(UnytsContext* ctx);

int    unyts_convert(UnytsContext* ctx,
                     double value,
                     const char* from_unit,
                     const char* to_unit,
                     double* out_value,
                     char* out_path,
                     int path_buf_len);

int    unyts_convertible(UnytsContext* ctx,
                         const char* from_unit,
                         const char* to_unit);

int    unyts_all_units(UnytsContext* ctx,
                       char* out_buf,
                       int buf_len);

void   unyts_set_fvf(UnytsContext* ctx, double fvf);
double unyts_get_fvf(UnytsContext* ctx);

#ifdef __cplusplus
}
#endif
```

### 5.8 pybind11 Python Bindings (`bindings_python/bindings.cpp`)

A pybind11 extension module (`unyts_cpp`) that exposes the C++ engine to Python, enabling it to serve as a **drop-in backend for the existing `unyts` Python package**.

```cpp
// bindings_python/bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>          // automatic list/dict conversion
#include "unyts/converter.h"
#include "unyts/registry.h"
#include "unyts/parameters.h"

namespace py = pybind11;

PYBIND11_MODULE(unyts_cpp, m) {
    m.doc() = "unyts C++ engine — Python bindings via pybind11";

    // Core conversion functions
    m.def("convert",
          [](double value, const std::string& from, const std::string& to) {
              unyts::Parameters params;
              auto result = unyts::convert(value, from, to, params);
              if (!result.success)
                  throw py::value_error(result.error_msg);
              return py::make_tuple(result.value, result.path_str);
          },
          py::arg("value"), py::arg("from_unit"), py::arg("to_unit"),
          "Convert a value between units. Returns (result, path_string).");

    m.def("convertible",
          [](const std::string& from, const std::string& to) {
              unyts::Parameters params;
              return unyts::convertible(from, to, params);
          },
          py::arg("from_unit"), py::arg("to_unit"));

    m.def("all_units",
          []() { return unyts::Registry::instance().all_units(); },
          "Return a list of all known unit names and aliases.");

    // Parameters
    py::class_<unyts::Parameters>(m, "Parameters")
        .def(py::init<>())
        .def_readwrite("algorithm",   &unyts::Parameters::algorithm)
        .def_readwrite("timeout_ms",  &unyts::Parameters::timeout_ms)
        .def_readwrite("fvf",         &unyts::Parameters::fvf)
        .def_readwrite("print_path",  &unyts::Parameters::print_path)
        .def_readwrite("verbose",     &unyts::Parameters::verbose)
        .def_readwrite("raise_error", &unyts::Parameters::raise_error);
}
```

**How this integrates with the existing Python package:**

Once the module is built, the existing `converter.py` can delegate to it with a one-line change:

```python
# src/unyts/converter.py  (future version)
try:
    from unyts_cpp import convert as _cpp_convert, convertible as _cpp_convertible
    _USE_CPP_ENGINE = True
except ImportError:
    _USE_CPP_ENGINE = False  # graceful fallback to pure-Python

def convert(value, from_unit, to_unit, ...):
    if _USE_CPP_ENGINE:
        result, path = _cpp_convert(value, from_unit, to_unit)
        return result
    # ... existing pure-Python implementation
```

This means:
- The C++ engine is **opt-in**: if `unyts_cpp.pyd` is present it is used automatically; otherwise the pure-Python engine runs unchanged
- Existing user code (`from unyts import convert`) requires **zero changes**
- The `unyts_cpp` wheel can be distributed as an optional dependency: `pip install unyts[fast]`

**CMakeLists.txt snippet:**
```cmake
find_package(pybind11 REQUIRED)  # via vcpkg
pybind11_add_module(unyts_cpp bindings_python/bindings.cpp)
target_link_libraries(unyts_cpp PRIVATE unyts_core)
```

### 5.9 Qt Windows GUI

Port of `gui.py` (~779 lines, tkinter).

Widgets needed (maps 1:1 to Python GUI):
- `QComboBox` + `QCompleter` for unit autocomplete (replaces `ttk.Entry` + `_all_units_str`)
- `QDoubleSpinBox` or `QLineEdit` for value inputs
- `QPushButton` "Convert" + keyboard shortcut (Enter)
- `QCheckBox` "repeat search"
- `QLabel` result display
- `QLabel` / `QScrollingLabel` for path marquee
- Menu bar: File (load/save memory, settings), Help (documentation, about)

Recommended Qt approach: **Qt Widgets** (not QML) for a lightweight, Windows-native look; easier to migrate from tkinter one-widget-at-a-time.

---

## 6. Project Structure

```
unyts/
├── CMakeLists.txt               ← top-level; selects platform sub-targets
├── cmake/
│   ├── Toolchain-iOS.cmake
│   └── Toolchain-Android.cmake
├── core/                        ← shared C++ engine (all platforms)
│   ├── CMakeLists.txt
│   ├── include/unyts/
│   │   ├── graph.h
│   │   ├── search.h
│   │   ├── registry.h
│   │   ├── converter.h
│   │   ├── parameters.h
│   │   ├── database.h
│   │   └── unyts_capi.h         ← C API
│   └── src/
│       ├── graph.cpp
│       ├── search.cpp
│       ├── registry.cpp
│       ├── conversions.cpp      ← ported def_conversions.py
│       ├── prefixes.cpp
│       ├── converter.cpp
│       ├── parameters.cpp
│       └── database.cpp
├── bindings_python/             ← pybind11 Python extension module
│   ├── CMakeLists.txt
│   └── bindings.cpp             ← exposes C++ API as unyts_cpp Python module
├── gui_windows/                 ← Qt 6 Windows GUI
│   ├── CMakeLists.txt
│   ├── main.cpp
│   ├── MainWindow.h/.cpp
│   └── resources/
│       └── unyts_icon.ico
├── bridge_ios/                  ← Obj-C++ bridge (see iOS plan)
│   ├── UnytsWrapper.h
│   └── UnytsWrapper.mm
├── bridge_android/              ← JNI bridge (see Android plan)
│   └── unyts_jni.cpp
└── tests/
    ├── CMakeLists.txt
    └── test_core.cpp            ← mirrors Python pytest suite
```

---

## 7. Phased Delivery Plan

### Phase 0 — Environment Setup (1–2 weeks)
- Install Qt 6, CMake, MSVC (Visual Studio Build Tools), vcpkg
- Set up CMake project skeleton: `core/`, `gui_windows/`, `tests/`
- Configure CI (GitHub Actions) for Windows builds
- Verify cross-compilation to Android (NDK) and iOS (Xcode) works from the same CMakeLists — even before any code is written

### Phase 1 — Core Graph Engine (3–4 weeks)
- Implement `UNode`, `UDigraph`, `Conversion` in `graph.h/.cpp`
- Implement BFS, DFS, hybrid_BFS in `search.h/.cpp`
- Unit tests: port `tests/test_network.py` and `tests/test_searches.py`
- **Milestone**: search algorithms find shortest paths in a hand-built test graph

### Phase 2 — Unit Registry + Conversions (4–6 weeks)
- Implement `registry.h/.cpp` with all unit categories
- Port `def_conversions.py` (~200 conversion functions) → `conversions.cpp`
- Port `def_prefixes.py` (SI prefixes) → `prefixes.cpp`
- Populate the graph from the registry in `database.cpp`
- Unit tests: mirror `tests/test_dictionaries.py`, `tests/test_converter.py`
- **Milestone**: `convert(1.0, "meter", "foot")` returns correct result

### Phase 3 — Converter + Parameters (2–3 weeks)
- Implement `converter.h/.cpp` — `convert()`, `convertible()`, ambiguous-alias checks
- Implement `parameters.h/.cpp` — INI load/save, FVF, algorithm selector, timeout
- Implement `database.h/.cpp` — JSON search-path memory cache
- Unit tests: port `tests/test_parameters.py`, `tests/test_errors.py`
- **Milestone**: full regression suite of conversions passes

### Phase 4 — C API Surface (1 week)
- Write `unyts_capi.h/.cpp` wrapping the C++ API in a stable C interface
- Verify the C API from a separate C test program
- **Milestone**: `unyts_convert()` callable from plain C

### Phase 5 — Qt Windows GUI (3–4 weeks)
- Implement `MainWindow` with all widgets (unit entry, value, convert button, result label, path marquee)
- Wire up autocomplete for unit names using `QCompleter` + `QStringListModel`
- Add menu bar: settings (algorithm, timeout, FVF), memory (load/save/clean), help
- Windows installer via CPack + WiX
- **Milestone**: functional desktop app, feature-parity with `gui.py`

### Phase 6 — pybind11 Python Bindings (1–2 weeks)
- Add `bindings_python/bindings.cpp` with pybind11 module definition
- Wire `unyts.converter` to fall back gracefully: use `unyts_cpp` if present, pure-Python otherwise
- Build a Python wheel (`python -m build`) and verify `pip install dist/unyts_cpp-*.whl`
- Run the **existing Python pytest suite** against the C++ engine — this is the ultimate integration test
- Package as an optional `unyts[fast]` extra in `pyproject.toml`
- **Milestone**: `pytest tests/` passes 100% using the C++ engine instead of pure Python

### Phase 7 — Polish + Testing (2–3 weeks)
- End-to-end regression tests (port all Python tests)
- Performance benchmarks (BFS in C++ should be 10–100x faster than Python)
- Windows-specific testing: DPI scaling, Windows 10/11, MSVC runtime distribution
- Documentation: README for building from source, user-facing help

---

## 8. Effort Estimate

| Phase | Duration | Notes |
|---|---|---|
| 0 — Environment setup | 1–2 weeks | One-time investment |
| 1 — Graph engine | 3–4 weeks | Algorithmic; tests critical |
| 2 — Unit registry + conversions | 4–6 weeks | **Largest chunk**; mostly mechanical porting of ~200 conversion functions |
| 3 — Converter + parameters | 2–3 weeks | Logic-heavy; many edge cases |
| 4 — C API surface | 1 week | Thin wrapper; low risk |
| 5 — Qt GUI | 3–4 weeks | UI is not complex but Qt learning curve |
| 6 — pybind11 bindings | 1–2 weeks | Small binding file; pytest suite validates correctness |
| 7 — Polish + testing | 2–3 weeks | Quality gate |
| **Total** | **~5–7 months** | Single experienced C++ developer |

> **Parallelism opportunity**: Phases 1–4 (core) can overlap with Phase 5 (GUI) once Phase 1 is complete — a second developer can start the Qt skeleton while the core is being built.  With two developers the timeline shortens to ~3–4 months.

---

## 9. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| FVF-dependent conversions rely on mutable global state | Medium | High | Pass `Parameters&` explicitly through the call stack; avoid C globals in the API |
| Python's `cloudpickle` serializes lambdas; C++ has no equivalent | High | Medium | Rebuild graph from code on startup (fast); persist only BFS path-memory as JSON |
| Qt LGPL licensing requires dynamic linking or source disclosure | Low | Medium | Link Qt dynamically (default); include Qt attribution in About dialog |
| Large number of unit aliases causes startup performance issues | Low | Low | Build alias lookup map at compile time using `constexpr` tables |
| BFS on deep paths (FVF chains) could be slow | Low | Medium | Implement `deadline` parameter; hybrid_BFS as fallback |
| Cross-compilation to iOS/Android introduces platform-specific issues | Medium | Medium | Test early (Phase 0) before committing to the architecture |
| Ambiguous alias resolution logic is complex | Medium | Medium | Port `collect_alias_conflicts()` and `ALIAS_PRIORITY` map verbatim; add regression tests |

---

## 10. Prerequisites / Tools Required

- **Visual Studio 2022** (Community is free) — MSVC compiler
- **CMake 3.21+** — build orchestration
- **Qt 6.7+** — download from qt.io (LGPL option)
- **vcpkg** — dependency manager (nlohmann/json, Catch2, inih)
- **Git** — already in use
- Optional: **Qt Creator** IDE for GUI development
- Optional: **Ninja** build tool (faster than MSBuild)

---

## 11. Testing Strategy

- Every Python `pytest` test in `tests/` should have a C++ equivalent in `tests/test_core.cpp`
- Use Catch2 for unit tests (similar BDD-style to pytest)
- CI: GitHub Actions matrix: `windows-latest` (MSVC), `ubuntu-latest` (GCC), `macos-latest` (Clang/AppleClang) — the last two validate portability to mobile targets
- Coverage: aim for the same category coverage as the existing Python suite

---

## 12. Dependency Summary

```
vcpkg.json
{
  "dependencies": [
    "nlohmann-json",   // cache persistence
    "catch2",          // unit tests
    "inih",            // INI file parser for parameters
    "pybind11"         // Python bindings
  ]
}
```

Qt 6 installed separately via the Qt online installer (not vcpkg, to maintain LGPL compliance).

`pybind11` is also available via `pip install pybind11` — either source works with CMake's `find_package(pybind11)`.
