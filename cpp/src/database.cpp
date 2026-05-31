// unyts/database.cpp — full unit registry and conversion graph (Phase 2).
//
// Faithfully ports:
//   src/unyts/dictionaries.py   — unit catalogue (aliases, names, categories)
//   src/unyts/database.py       — graph-building logic (_load_network)
//   src/unyts/units/def_prefixes.py — SI / OGF / DATA prefix scale functions
//
// The graph is built once via std::call_once and cached in a static UDigraph.
// FVF-dependent edges (reservoir ↔ standard volumes) use a lambda that reads
// the graph's fvf field at conversion time.

#include "unyts/database.hpp"
#include "unyts/binary_cache.hpp"
#include "unyts/graph.hpp"
#include "unyts/aliases.hpp"
#include "unyts/conversions.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <mutex>
#include <set>
#include <string>
#include <unordered_set>
#include <vector>

namespace unyts {

// ─────────────────────────────────────────────────────────────────────────────
// Prefix scale tables — mirror def_prefixes.py
// ─────────────────────────────────────────────────────────────────────────────

struct SIPrefix { const char* symbol; double s1, s2, s3; };

static const SIPrefix kSI[] = {
    {"Q",  1e30, 1e60, 1e90}, {"R",  1e27, 1e54, 1e81},
    {"Y",  1e24, 1e48, 1e72}, {"Z",  1e21, 1e42, 1e63},
    {"E",  1e18, 1e36, 1e54}, {"P",  1e15, 1e30, 1e45},
    {"T",  1e12, 1e24, 1e36}, {"G",  1e9,  1e18, 1e27},
    {"M",  1e6,  1e12, 1e18},
    {"K",  1e3,  1e3,  1e3 }, // uppercase K: only linear scale
    {"k",  1e3,  1e6,  1e9 }, {"h",  1e2,  1e4,  1e6 },
    {"da", 1e1,  1e2,  1e3 }, {"d",  1e-1, 1e-2, 1e-3},
    {"c",  1e-2, 1e-4, 1e-6}, {"m",  1e-3, 1e-6, 1e-9},
    {"\xc2\xb5", 1e-6, 1e-12, 1e-18}, {"u",  1e-6, 1e-12, 1e-18},
    {"n",  1e-9, 1e-18, 1e-27}, {"p",  1e-12, 1e-24, 1e-36},
    {"f",  1e-15,1e-30, 1e-45}, {"a",  1e-18, 1e-36, 1e-54},
    {"z",  1e-21,1e-42, 1e-63}, {"y",  1e-24, 1e-48, 1e-72},
    {"r",  1e-27,1e-54, 1e-81}, {"q",  1e-30, 1e-60, 1e-90},
};
static const SIPrefix kSI_butK[] = {
    {"Q",  1e30, 1e60, 1e90}, {"R",  1e27, 1e54, 1e81},
    {"Y",  1e24, 1e48, 1e72}, {"Z",  1e21, 1e42, 1e63},
    {"E",  1e18, 1e36, 1e54}, {"P",  1e15, 1e30, 1e45},
    {"T",  1e12, 1e24, 1e36}, {"G",  1e9,  1e18, 1e27},
    {"M",  1e6,  1e12, 1e18},
    {"k",  1e3,  1e6,  1e9 }, {"h",  1e2,  1e4,  1e6 },
    {"da", 1e1,  1e2,  1e3 }, {"d",  1e-1, 1e-2, 1e-3},
    {"c",  1e-2, 1e-4, 1e-6}, {"m",  1e-3, 1e-6, 1e-9},
    {"\xc2\xb5", 1e-6, 1e-12, 1e-18}, {"u",  1e-6, 1e-12, 1e-18},
    {"n",  1e-9, 1e-18, 1e-27}, {"p",  1e-12, 1e-24, 1e-36},
    {"f",  1e-15,1e-30, 1e-45}, {"a",  1e-18, 1e-36, 1e-54},
    {"z",  1e-21,1e-42, 1e-63}, {"y",  1e-24, 1e-48, 1e-72},
    {"r",  1e-27,1e-54, 1e-81}, {"q",  1e-30, 1e-60, 1e-90},
};

struct OGFPrefix { const char* symbol; double s3; };
static const OGFPrefix kOGF[] = {
    {"M",  1e3}, {"MM", 1e6}, {"B",  1e9}, {"T",  1e12},
};

struct DATAPrefix { const char* symbol; double s_bit; double s_byte; };
static const DATAPrefix kDATA[] = {
    {"Y", 1e24,                std::pow(2.0, 80)},
    {"Z", 1e21,                std::pow(2.0, 70)},
    {"E", 1e18,                std::pow(2.0, 60)},
    {"P", 1e15,                std::pow(2.0, 50)},
    {"T", 1e12,                std::pow(2.0, 40)},
    {"G", 1e9,                 std::pow(2.0, 30)},
    {"M", 1e6,                 std::pow(2.0, 20)},
    {"K", 1e3,                 std::pow(2.0, 10)},
    {"k", 1e3,                 std::pow(2.0, 10)},
};

static const std::unordered_set<std::string> kSI_order2 = { "Area" };
static const std::unordered_set<std::string> kSI_order3 = { "Rate", "Volume" };

static bool is_protected(const char* prefix, const std::string& base) {
    if (std::string(prefix) == "r" &&
        (base == "m3" || base == "m\xc2\xb3" || base == "m^3"))
        return true;
    return false;
}

// ─────────────────────────────────────────────────────────────────────────────
// Graph-builder helpers
// ─────────────────────────────────────────────────────────────────────────────

static inline void add_node_safe(UDigraph& g, const std::string& name) {
    if (!g.has_node(name)) g.add_node(UNode{name});
}

static inline void add_edge_safe(UDigraph& g,
                                  const std::string& src,
                                  const std::string& dest,
                                  ConvFn fn,
                                  bool rev = false,
                                  bool alias_flag = false) {
    add_node_safe(g, src);
    add_node_safe(g, dest);
    const UNode* s = g.get_node(src);
    const UNode* d = g.get_node(dest);
    if (!s || !d) return;
    g.add_edge(Conversion{*s, *d, std::move(fn), rev, alias_flag});
}

static void alias_pair(UDigraph& g, AliasRegistry& reg,
                        const std::string& a, const std::string& b) {
    add_node_safe(g, a);
    add_node_safe(g, b);
    add_edge_safe(g, a, b, equality, false, true);
    add_edge_safe(g, b, a, equality, false, true);
    reg.add_synonym(a, b);
    reg.add_synonym(b, a);
}

static void fn_pair(UDigraph& g,
                    const std::string& from, ConvFn fwd,
                    const std::string& to,   ConvFn rev_fn) {
    add_node_safe(g, from);
    add_node_safe(g, to);
    add_edge_safe(g, from, to, std::move(fwd));
    add_edge_safe(g, to,   from, std::move(rev_fn));
}

static void apply_si_prefixes(UDigraph& g,
                               const std::string& base,
                               const std::string& category,
                               bool use_K = true) {
    const SIPrefix* prefixes = use_K ? kSI : kSI_butK;
    size_t count = use_K ? std::size(kSI) : std::size(kSI_butK);
    int order = 1;
    if (kSI_order2.count(category)) order = 2;
    else if (kSI_order3.count(category)) order = 3;

    for (size_t i = 0; i < count; ++i) {
        const SIPrefix& p = prefixes[i];
        if (is_protected(p.symbol, base)) continue;
        std::string pname = std::string(p.symbol) + base;
        double scale = (order == 1) ? p.s1 : (order == 2) ? p.s2 : p.s3;
        add_node_safe(g, pname);
        add_node_safe(g, base);
        add_edge_safe(g, pname, base, [scale](double x){ return x * scale; });
        add_edge_safe(g, base, pname, [scale](double x){ return x / scale; });
    }
}

static void apply_ogf_prefixes(UDigraph& g, const std::string& base) {
    for (const auto& p : kOGF) {
        std::string pname = std::string(p.symbol) + base;
        double scale = p.s3;
        add_node_safe(g, pname);
        add_node_safe(g, base);
        add_edge_safe(g, pname, base, [scale](double x){ return x * scale; });
        add_edge_safe(g, base, pname, [scale](double x){ return x / scale; });
    }
}

static void apply_data_prefixes_bit(UDigraph& g, const std::string& base) {
    for (const auto& p : kDATA) {
        std::string pname = std::string(p.symbol) + base;
        double scale = p.s_bit;
        add_node_safe(g, pname);
        add_node_safe(g, base);
        add_edge_safe(g, pname, base, [scale](double x){ return x * scale; });
        add_edge_safe(g, base, pname, [scale](double x){ return x / scale; });
    }
}

static void apply_data_prefixes_byte(UDigraph& g, const std::string& base) {
    for (const auto& p : kDATA) {
        std::string pname = std::string(p.symbol) + base;
        double scale = p.s_byte;
        add_node_safe(g, pname);
        add_node_safe(g, base);
        add_edge_safe(g, pname, base, [scale](double x){ return x * scale; });
        add_edge_safe(g, base, pname, [scale](double x){ return x / scale; });
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// populate_graph — main entry point
// ─────────────────────────────────────────────────────────────────────────────

void populate_graph(UDigraph& g) {
    AliasRegistry& reg = global_alias_registry();

    // Convenience lambda: alias with registration
    auto al = [&](const std::string& a, const std::string& b) {
        alias_pair(g, reg, a, b);
    };

    // ─────────────────────────────────────────────────────────────────────────
    // 1. DIMENSIONLESS / FRACTION
    // ─────────────────────────────────────────────────────────────────────────
    add_node_safe(g, "fraction");
    add_node_safe(g, "percentage");
    al("fraction",   "ratio");
    al("fraction",   "dimensionless");
    al("fraction",   "unitless");
    al("percentage", "%");
    al("percentage", "perc");
    al("percentage", "percent");
    al("percentage", "/100");
    fn_pair(g, "fraction",   fraction__to__percentage, "percentage", percentage__to__fraction);

    // ─────────────────────────────────────────────────────────────────────────
    // 2. TIME
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"nanosecond","millisecond","second","minute","hour",
                    "day","week","month","year","lustrum","decade","century"})
        add_node_safe(g, n);

    al("nanosecond", "ns");
    al("millisecond","ms");
    al("second","s");  al("second","sec");
    al("minute","min");
    al("hour","h");    al("hour","hr");
    al("day","d");
    al("week","we");   al("week","wk");
    al("month","mo");
    al("year","y");    al("year","yr");

    // SI prefixes on "s"
    apply_si_prefixes(g, "s", "Time");

    // nanosecond/millisecond use SI prefix edges (ns,ms) + alias — no direct edge needed
    fn_pair(g, "minute",  minute__to__second,       "second", [](double t){ return t/60.0; });
    fn_pair(g, "hour",    hour__to__minute,          "minute", [](double t){ return t/60.0; });
    fn_pair(g, "day",     day__to__hour,              "hour",   [](double t){ return t/24.0; });
    fn_pair(g, "week",    week__to__day,              "day",    [](double t){ return t/7.0; });
    fn_pair(g, "day",     day__to__month,             "month",  [](double t){ return t*365.25/12.0; });
    fn_pair(g, "year",    year__to__month,            "month",  [](double t){ return t/12.0; });
    fn_pair(g, "year",    year__to__day,              "day",    [](double t){ return t*100.0/36525.0; });
    fn_pair(g, "lustrum", lustrum__to__year,          "year",   [](double t){ return t/5.0; });
    fn_pair(g, "decade",  decade__to__year,           "year",   [](double t){ return t/10.0; });
    fn_pair(g, "century", century__to__year,          "year",   [](double t){ return t/100.0; });

    // Frequency
    add_node_safe(g,"Hertz"); apply_si_prefixes(g,"Hz","Frequency");
    al("Hertz","Hz"); al("Hertz","1/s"); al("Hertz","s-1"); al("Hertz","s^-1");
    add_node_safe(g,"RPM"); al("RPM","rpm"); al("RPM","1/min"); al("RPM","min-1");

    // ─────────────────────────────────────────────────────────────────────────
    // 3. TEMPERATURE
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"Celsius","Fahrenheit","Rankine","Kelvin"}) add_node_safe(g, n);

    al("Celsius",    "Centigrade"); al("Celsius","C");    al("Celsius","degC");
    al("Celsius",    "deg C");      al("Celsius","degrees C");
    al("Fahrenheit", "F");          al("Fahrenheit","degF"); al("Fahrenheit","deg F");
    al("Rankine",    "R");          al("Rankine","degR");    al("Rankine","deg R");
    al("Kelvin",     "K");          al("Kelvin","degK");     al("Kelvin","deg K");

    fn_pair(g, "Celsius",    Celsius__to__Kelvin,      "Kelvin",     Kelvin__to__Celsius);
    fn_pair(g, "Celsius",    Celsius__to__Fahrenheit,  "Fahrenheit", Fahrenheit__to__Celsius);
    fn_pair(g, "Fahrenheit", Fahrenheit__to__Rankine,  "Rankine",    Rankine__to__Fahrenheit);
    fn_pair(g, "Rankine",    Rankine__to__Kelvin,      "Kelvin",     Kelvin__to__Rankine);

    // ─────────────────────────────────────────────────────────────────────────
    // 4. LENGTH
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"meter","thou","tenth","inch","foot","yard","chain","rod",
                    "furlong","mile","league","nautical mile","nautical league",
                    "astronomical unit","parsec","light year","scandinavian mile"})
        add_node_safe(g, n);

    apply_si_prefixes(g, "m", "Length");

    al("meter",  "m");     al("meter","metre");  al("meter","metro");
    al("kilometer","km");  al("kilometer","kilometre");
    al("centimeter","cm"); al("centimeter","centimetre");
    al("millimeter","mm"); al("millimeter","millimetre");
    al("micrometer","\xce\xbcm"); al("micrometer","um"); al("micrometer","micrometre");
    al("nanometer","nm");  al("nanometer","nanometre");
    al("thou",   "th");
    al("tenth",  "te");    al("tenth","0.1 in"); al("tenth",".1in");
    al("inch",   "in");    al("inch","\"");
    al("foot",   "feet");  al("foot","ft");       al("foot","'");
    al("yard",   "yd");
    al("chain",  "ch");
    al("rod",    "rd");
    al("furlong","fur");
    al("mile",   "mi");
    al("league", "lea");
    al("nautical mile","nmi");
    al("nautical league","nlea");
    al("astronomical unit","au");
    al("light year","ly");    al("light year","lyr");
    al("scandinavian mile","mil");

    fn_pair(g, "yard",    yard__to__meter,   "meter",  [](double d){ return d/0.9144; });
    fn_pair(g, "foot",    foot__to__meter,   "meter",  [](double d){ return d/0.3048; });
    fn_pair(g, "nautical mile", nautical_mile__to__meter, "meter", [](double d){ return d/1852.0; });
    fn_pair(g, "astronomical unit", astronomical_unit__to__meter, "meter",
               [](double d){ return d/149597870700.0; });
    fn_pair(g, "parsec",  parsec__to__astronomical_unit, "astronomical unit", [](double d){ return d/206265.0; });
    fn_pair(g, "light year", light_year__to__meter, "meter",
               [](double d){ return d/(kSpeedOfLight*365.25*24.0*3600.0); });
    fn_pair(g, "scandinavian mile", scandinavian_mile__to__kilometer, "km", [](double d){ return d/10.0; });
    fn_pair(g, "inch",   inch__to__thou,     "thou",    [](double d){ return d/1000.0; });
    fn_pair(g, "inch",   inch__to__tenth,    "tenth",   [](double d){ return d/10.0; });
    fn_pair(g, "foot",   foot__to__inch,     "inch",    [](double d){ return d/12.0; });
    fn_pair(g, "yard",   yard__to__foot,     "foot",    [](double d){ return d/3.0; });
    fn_pair(g, "chain",  chain__to__yard,    "yard",    [](double d){ return d/22.0; });
    fn_pair(g, "rod",    rod__to__yard,      "yard",    [](double d){ return d*10.0/55.0; });
    fn_pair(g, "furlong",furlong__to__chain, "chain",   [](double d){ return d/10.0; });
    fn_pair(g, "mile",   mile__to__furlong,  "furlong", [](double d){ return d/8.0; });
    fn_pair(g, "league", league__to__mile,   "mile",    [](double d){ return d/3.0; });
    fn_pair(g, "nautical league", nautical_league__to__nautical_mile,
               "nautical mile", [](double d){ return d/3.0; });

    // ─────────────────────────────────────────────────────────────────────────
    // 5. AREA
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"square meter","square centimeter","square kilometer",
                    "acre","square thou","square tenth","square inch","square foot",
                    "square yard","square chain","square rod","square furlong",
                    "square mile","square league"})
        add_node_safe(g, n);

    apply_si_prefixes(g, "m2",   "Area");
    apply_si_prefixes(g, "m\xc2\xb2", "Area");
    apply_si_prefixes(g, "m^2",  "Area");

    al("square meter","m2"); al("square meter","m\xc2\xb2"); al("square meter","m^2");
    al("square meter","sq m"); al("square meter","sqm"); al("square meter","centiare");
    al("square centimeter","cm2"); al("square centimeter","cm\xc2\xb2"); al("square centimeter","cm^2");
    al("square kilometer","km2"); al("square kilometer","km\xc2\xb2"); al("square kilometer","km^2");
    al("square foot","ft2"); al("square foot","ft\xc2\xb2"); al("square foot","ft^2");
    al("square foot","sq ft"); al("square foot","sqft");
    al("square inch","in2"); al("square inch","in\xc2\xb2"); al("square inch","in^2");
    al("square yard","yd2"); al("square yard","yd\xc2\xb2"); al("square yard","yd^2");
    al("square mile","mi2"); al("square mile","mi\xc2\xb2"); al("square mile","mi^2");

    fn_pair(g,"square league",   square_league__to__square_mile,   "square mile",    [](double d){ return d/9.0; });
    fn_pair(g,"square mile",     square_mile__to__square_furlong,  "square furlong", [](double d){ return d/64.0; });
    fn_pair(g,"square furlong",  square_furlong__to__square_chain, "square chain",   [](double d){ return d/100.0; });
    fn_pair(g,"square chain",    square_chain__to__square_yard,    "square yard",    [](double d){ return d/484.0; });
    fn_pair(g,"square rod",      square_rod__to__square_yard,      "square yard",    [](double d){ return d*100.0/3025.0; });
    fn_pair(g,"square mile",     square_mile__to__acre,            "acre",           [](double d){ return d/640.0; });
    fn_pair(g,"acre",            acre__to__square_yard,            "square yard",    [](double d){ return d/4840.0; });
    fn_pair(g,"square yard",     square_yard__to__square_foot,     "square foot",    [](double d){ return d/9.0; });
    fn_pair(g,"square foot",     square_foot__to__square_inch,     "square inch",    [](double d){ return d/144.0; });
    fn_pair(g,"square foot",     square_foot__to__square_meter,    "square meter",   [](double d){ return d/(0.3048*0.3048); });
    fn_pair(g,"square kilometer",square_kilometer__to__square_meter,"square meter",  [](double d){ return d/1e6; });
    fn_pair(g,"square inch",     square_inch__to__square_thou,     "square thou",    [](double d){ return d/1e6; });
    fn_pair(g,"square inch",     square_inch__to__square_tenth,    "square tenth",   [](double d){ return d/100.0; });

    // ─────────────────────────────────────────────────────────────────────────
    // 6. VOLUME
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {
        "cubic meter","cubic centimeter","litre","millilitre",
        "standard cubic meter","reservoir cubic meter",
        "cubic inch","cubic foot","cubic yard","cubic chain",
        "cubic furlong","cubic mile","cubic league","cubic thou","cubic tenth",
        "fluid ounce","gill","pint","quart","gallonUS",
        "gallonUK","fluid ounce UK","gillUK","pintUK","quartUK",
        "barrel","standard barrel","reservoir barrel","standard cubic foot"
    }) add_node_safe(g, n);

    apply_si_prefixes(g, "m3",  "Volume");
    apply_si_prefixes(g, "m\xc2\xb3", "Volume");
    apply_si_prefixes(g, "m^3", "Volume");
    // linearSI for reservoir/standard volumes (always order 1)
    for (auto& base : {"sm3","stm3","rem3","l"}) {
        for (const auto& p : kSI) {
            if (is_protected(p.symbol, base)) continue;
            std::string pname = std::string(p.symbol) + base;
            double scale = p.s1;
            add_node_safe(g, pname); add_node_safe(g, base);
            add_edge_safe(g, pname, base, [scale](double x){ return x*scale; });
            add_edge_safe(g, base, pname, [scale](double x){ return x/scale; });
        }
    }
    for (auto& b : {"scf","cf","ft3","stb","bbl","rb","reb","stbo","stbw"})
        apply_ogf_prefixes(g, b);

    al("cubic meter","m3"); al("cubic meter","m\xc2\xb3"); al("cubic meter","m^3"); al("cubic meter","CM");
    al("cubic centimeter","cm3"); al("cubic centimeter","cc"); al("cubic centimeter","cm^3");
    al("standard cubic meter","sm3"); al("standard cubic meter","Sm3"); al("standard cubic meter","stm3");
    al("standard cubic meter","sm\xc2\xb3"); al("standard cubic meter","sm^3");
    al("reservoir cubic meter","rem3"); al("reservoir cubic meter","REm3"); al("reservoir cubic meter","rm3");
    al("reservoir cubic meter","rem\xc2\xb3"); al("reservoir cubic meter","rem^3"); al("reservoir cubic meter","RM3");
    al("litre","l"); al("litre","liter"); al("litre","litro");
    al("millilitre","ml"); al("millilitre","milliliter");
    al("cubic foot","ft3"); al("cubic foot","ft\xc2\xb3"); al("cubic foot","ft^3");
    al("cubic foot","cf"); al("cubic foot","pc"); al("cubic foot","pie cubico");
    al("standard cubic foot","scf");
    al("cubic inch","in3"); al("cubic inch","in\xc2\xb3"); al("cubic inch","in^3");
    al("cubic yard","yd3"); al("cubic yard","yd\xc2\xb3"); al("cubic yard","yd^3");
    al("barrel","bbl"); al("barrel","stb");
    al("standard barrel","stb"); al("standard barrel","stbo"); al("standard barrel","stbw");
    al("reservoir barrel","rb"); al("reservoir barrel","reb");
    al("fluid ounce","fl oz"); al("fluid ounce","ozUS");
    al("gallonUS","gal"); al("gallonUS","galUS"); al("gallonUS","USgal"); al("gallonUS","gallon");
    al("gallonUK","galUK"); al("gallonUK","UKgal"); al("gallonUK","imperial gallon");
    al("fluid ounce UK","fl oz UK"); al("fluid ounce UK","ozUK");

    fn_pair(g,"litre",         litre__to__cubic_centimeter,  "cubic centimeter", [](double v){ return v/1000.0; });
    fn_pair(g,"gill",          gill__to__fluid_ounce,        "fluid ounce",      [](double v){ return v/4.0; });
    fn_pair(g,"pint",          pint__to__gill,               "gill",             [](double v){ return v/4.0; });
    fn_pair(g,"quart",         quart__to__pint,              "pint",             [](double v){ return v/2.0; });
    fn_pair(g,"gallonUS",      gallonUS__to__quart,          "quart",            [](double v){ return v/4.0; });
    fn_pair(g,"gallonUS",      gallonUS__to__fluid_ounce,    "fluid ounce",      [](double v){ return v/128.0; });
    fn_pair(g,"gallonUS",      gallonUS__to__cubic_inch,     "cubic inch",       [](double v){ return v/231.0; });
    fn_pair(g,"gallonUK",      gallonUK__to__quartUK,        "quartUK",          [](double v){ return v/4.0; });
    fn_pair(g,"gallonUK",      gallonUK__to__fluid_ounce_UK, "fluid ounce UK",   [](double v){ return v/160.0; });
    fn_pair(g,"gallonUK",      gallonUK__to__litre,          "litre",            [](double v){ return v/4.54609; });
    fn_pair(g,"gillUK",        gillUK__to__fluid_ounce_UK,   "fluid ounce UK",   [](double v){ return v/4.0; });
    fn_pair(g,"pintUK",        pintUK__to__gillUK,           "gillUK",           [](double v){ return v/4.0; });
    fn_pair(g,"quartUK",       quartUK__to__pintUK,          "pintUK",           [](double v){ return v/2.0; });
    fn_pair(g,"cubic foot",    cubic_foot__to__cubic_meter,  "cubic meter",
               [](double v){ return v/std::pow(3048.0,3)*std::pow(10000.0,3); });
    fn_pair(g,"cubic foot",    cubic_foot__to__cubic_inch,   "cubic inch",       [](double v){ return v/1728.0; });
    fn_pair(g,"cubic yard",    cubic_yard__to__cubic_foot,   "cubic foot",       [](double v){ return v/27.0; });
    fn_pair(g,"cubic chain",   cubic_chain__to__cubic_yard,  "cubic yard",       [](double v){ return v/10648.0; });
    fn_pair(g,"cubic furlong", cubic_furlong__to__cubic_chain,"cubic chain",     [](double v){ return v/1000.0; });
    fn_pair(g,"cubic mile",    cubic_mile__to__cubic_furlong,"cubic furlong",    [](double v){ return v/512.0; });
    fn_pair(g,"cubic league",  cubic_league__to__cubic_mile, "cubic mile",       [](double v){ return v/27.0; });
    fn_pair(g,"cubic inch",    cubic_inch__to__cubic_thou,   "cubic thou",       [](double v){ return v/1e9; });
    fn_pair(g,"cubic inch",    cubic_inch__to__cubic_tenth,  "cubic tenth",      [](double v){ return v/1000.0; });
    fn_pair(g,"standard cubic foot", standard_cubic_foot__to__standard_cubic_meter,
               "standard cubic meter", standard_cubic_meter__to__standard_cubic_foot);
    fn_pair(g,"standard barrel",     standard_barrel__to__USgal,
               "gallonUS",           [](double v){ return v/42.0; });
    fn_pair(g,"standard cubic meter",standard_cubic_meter__to__standard_barrel,
               "standard barrel",    [](double v){ return v/6.289814; });
    fn_pair(g,"standard barrel",     standard_barrel__to__standard_cubic_foot,
               "standard cubic foot",[](double v){ return v/5.614584; });
    fn_pair(g,"reservoir cubic meter",reservoir_cubic_meter__to__reservoir_barrel,
               "reservoir barrel",   [](double v){ return v/6.289814; });

    // FVF-dependent edge
    UDigraph* gptr = &g;
    add_edge_safe(g, "reservoir cubic meter", "standard cubic meter",
        [gptr](double v) -> double {
            double fvf = (gptr->fvf > 0.0) ? gptr->fvf : 1.0;
            return v / fvf;
        });
    add_edge_safe(g, "standard cubic meter", "reservoir cubic meter",
        [gptr](double v) -> double {
            double fvf = (gptr->fvf > 0.0) ? gptr->fvf : 1.0;
            return v * fvf;
        });

    // ─────────────────────────────────────────────────────────────────────────
    // 7. PRESSURE
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"Pascal","absolute psi","psi gauge","absolute bar","bar gauge",
                    "atmosphere","Torr","millimeters of mercury","kilogram/square centimeter"})
        add_node_safe(g, n);

    apply_si_prefixes(g, "Pa",   "Pressure");
    apply_si_prefixes(g, "bara", "Pressure");
    apply_si_prefixes(g, "bar",  "Pressure");
    apply_si_prefixes(g, "barg", "Pressure");
    apply_si_prefixes(g, "psia", "Pressure");

    al("Pascal","Pa"); al("Pascal","N/m2"); al("Pascal","Newton/m2");
    al("absolute psi","psia"); al("absolute psi","psi absolute");
    al("psi gauge","psig"); al("absolute psi","pound/square inch");
    al("absolute bar","bara"); al("absolute bar","barsa");
    al("bar gauge","barg"); al("absolute bar","bars");
    al("atmosphere","atm"); al("atmosphere","atma");
    al("Torr","millimeters of mercury"); al("millimeters of mercury","mmHg");
    al("kilogram/square centimeter","kg/cm2"); al("kilogram/square centimeter","kg/cm^2");

    // 'bar' and 'psi' are intermediate nodes (matching the Python graph): each is 1:1
    // with BOTH its gauge and its absolute counterpart.  BFS then finds:
    //   bar→bara = 1.0  (bar→absolute bar, 1-hop equality, shorter than offset path)
    //   bar→barg = 1.0  (bar→bar gauge,    1-hop equality)
    //   barg→bara = 2.01325  (bar gauge→absolute bar, 1-hop offset, shorter than 2-hop via bar)
    // and likewise for psi/psia/psig.
    add_node_safe(g, "psi");
    add_edge_safe(g, "bar",          "bar gauge",    equality, false, true);
    add_edge_safe(g, "bar gauge",    "bar",          equality, false, true);
    add_edge_safe(g, "bar",          "absolute bar", equality, false, true);
    add_edge_safe(g, "absolute bar", "bar",          equality, false, true);
    add_edge_safe(g, "psi",          "psi gauge",    equality, false, true);
    add_edge_safe(g, "psi gauge",    "psi",          equality, false, true);
    add_edge_safe(g, "psi",          "absolute psi", equality, false, true);
    add_edge_safe(g, "absolute psi", "psi",          equality, false, true);

    fn_pair(g,"psi gauge",    psi_gauge__to__absolute_psi,  "absolute psi",   absolute_psi__to__psi_gauge);
    fn_pair(g,"bar gauge",    bar_gauge__to__absolute_bar,  "absolute bar",   absolute_bar__to__bar_gauge);
    fn_pair(g,"absolute bar", absolute_bar__to__absolute_psi,"absolute psi",  [](double p){ return p/14.50377377322; });
    fn_pair(g,"bar gauge",    bar_gauge__to__psi_gauge,     "psi gauge",      [](double p){ return p/14.50377377322; });
    fn_pair(g,"absolute bar", absolute_bar__to__Pascal,     "Pascal",         [](double p){ return p/100000.0; });
    fn_pair(g,"atmosphere",   atmosphere__to__Pascal,       "Pascal",         [](double p){ return p/101325.0; });
    fn_pair(g,"atmosphere",   atmosphere__to__Torr,         "Torr",           [](double p){ return p/760.0; });
    fn_pair(g,"atmosphere",   atmosphere__to__absolute_bar, "absolute bar",   [](double p){ return p*100000.0/101325.0; });
    fn_pair(g,"absolute bar", absolute_bar__to__kilogram_slash_square_centimeter,
               "kilogram/square centimeter", [](double p){ return p/(10.0/kStandardEarthGravity); });

    // Pressure gradient
    for (auto& n : {"psi/ft","psi/m","bar/m","bar/ft"}) add_node_safe(g, n);
    al("psi/ft","psia/ft"); al("psi/m","psia/m"); al("bar/m","bara/m"); al("bar/ft","bara/ft");

    // ─────────────────────────────────────────────────────────────────────────
    // 8. WEIGHT / MASS
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"gram","kilogram","milligram","microgram","metric ton",
                    "grain","pennyweight","dram","ounce","pound","stone","quarter",
                    "short hundredweight","long hundredweight","short ton","long ton"})
        add_node_safe(g, n);

    apply_si_prefixes(g, "g",     "Weight");
    apply_si_prefixes(g, "g-mol", "Weight");

    al("gram","g"); al("kilogram","kg"); al("milligram","mg");
    al("microgram","ug"); al("microgram","\xc2\xb5g");
    al("metric ton","Tonne");
    al("grain","gr");
    al("pennyweight","pwt"); al("pennyweight","dwt");
    al("dram","dr");
    al("ounce","oz"); al("ounce","wt oz"); al("ounce","weight ounce");
    al("pound","lb"); al("pound","#"); al("pound","libra");
    al("stone","st");
    al("long hundredweight","cwt");                         // cwt = UK long hundredweight (112 lb)
    al("short hundredweight","US hundredweight");
    al("long hundredweight","UK hundredweight");
    al("short ton","USton"); al("short ton","tonUS");
    al("long ton","UKton"); al("long ton","ton"); al("long ton","Ton");
    al("long ton","t");                                       // t = UK long ton in Python unyts
    al("metric ton","tonne"); al("metric ton","mt"); al("metric ton","MT");

    fn_pair(g,"grain",             grain__to__milligrams,            "milligram",          [](double w){ return w/64.7989; });
    fn_pair(g,"pennyweight",       pennyweight__to__grain,           "grain",              [](double w){ return w/24.0; });
    fn_pair(g,"dram",              dram__to__pound,                  "pound",              [](double w){ return w*256.0; });
    fn_pair(g,"stone",             stone__to__pound,                 "pound",              [](double w){ return w/14.0; });
    fn_pair(g,"quarter",           quarter__to__stone,               "stone",              [](double w){ return w/2.0; });
    fn_pair(g,"ounce",             weight_ounce__to__dram,           "dram",               [](double w){ return w/16.0; });
    fn_pair(g,"pound",             pound__to__weight_ounce,          "ounce",              [](double w){ return w/16.0; });
    fn_pair(g,"long hundredweight",long_hundredweight__to__quarter,  "quarter",            [](double w){ return w/4.0; });
    fn_pair(g,"short hundredweight",short_hundredweight__to__pound,  "pound",              [](double w){ return w/100.0; });
    fn_pair(g,"short ton",         short_ton__to__short_hundredweight,"short hundredweight",[](double w){ return w/20.0; });
    fn_pair(g,"long ton",          long_ton__to__long_hundredweight, "long hundredweight", [](double w){ return w/20.0; });
    fn_pair(g,"metric ton",        metric_ton__to__kilogram,         "kilogram",           [](double w){ return w/1000.0; });
    fn_pair(g,"kilogram",          kilogram__to__gram,               "gram",               [](double w){ return w/1000.0; });
    fn_pair(g,"pound",             pound__to__kilogram,              "kilogram",           [](double w){ return w*100000000.0/45359237.0; });

    // Mass (kilogram mass distinct from kilogram force)
    add_node_safe(g, "kilogram mass");
    al("kilogram mass","Kgm");
    alias_pair(g, reg, "kilogram mass", "kilogram");

    // ─────────────────────────────────────────────────────────────────────────
    // 9. FORCE
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"Newton","kilogram force","Dyne","pound force"}) add_node_safe(g, n);
    apply_si_prefixes(g, "N", "Force");
    al("Newton","N"); al("Newton","newton"); al("Newton","kg*m/s2"); al("Newton","kg*m/s^2");
    al("kilogram force","kgf"); al("kilogram force","kilopondio"); al("kilogram force","kp");
    al("Dyne","dyne"); al("Dyne","dyn");
    al("pound force","lbf");

    fn_pair(g,"kilogram mass",  kilogram_mass__to__kilogram_force, "kilogram force", kilogram_force__to__kilogram_mass);
    fn_pair(g,"kilogram force", kilogram_force__to__Newton,        "Newton",         [](double f){ return f/kStandardEarthGravity; });
    fn_pair(g,"Dyne",           Dyne__to__Newton,                  "Newton",         Newton__to__Dyne);

    // ─────────────────────────────────────────────────────────────────────────
    // 10. ENERGY
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"Joule","Kilojoule","kilowatt hour","British thermal unit",
                    "Watt second","Watt hour","gram calorie"})
        add_node_safe(g, n);

    apply_si_prefixes(g, "J",  "Energy");
    apply_si_prefixes(g, "Wh", "Energy");
    apply_si_prefixes(g, "Ws", "Energy");

    al("Joule","J");         al("Joule","N*m");       al("Joule","Watt second");
    al("Kilojoule","kJ");
    al("kilowatt hour","kWh"); al("kilowatt hour","kW*h");
    al("British thermal unit","BTU");
    al("Watt second","Ws");  al("Watt second","W*s");
    al("Watt hour","Wh");    al("Watt hour","W*h");
    al("gram calorie","cal"); al("gram calorie","calorie");

    fn_pair(g,"Joule",     Joule__to__gram_calorie,           "gram calorie",        [](double e){ return e*4.184; });
    fn_pair(g,"Kilojoule", Kilojoule__to__Joule,              "Joule",               [](double e){ return e/1000.0; });
    fn_pair(g,"Kilojoule", Kilojoule__to__kilowatt_hour,      "kilowatt hour",        kilowatt_hour__to__Kilojoule);
    fn_pair(g,"Kilojoule", Kilojoule__to__British_thermal_unit,"British thermal unit",[](double e){ return e*1.055; });
    fn_pair(g,"Watt second",Watt_second__to__Joule,           "Joule",               [](double e){ return e; });
    fn_pair(g,"Watt hour",  Watt_hour__to__Kilojoule,         "Kilojoule",           [](double e){ return e/3.6; });

    // ─────────────────────────────────────────────────────────────────────────
    // 11. POWER
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"Watt","Horsepower"}) add_node_safe(g, n);
    apply_si_prefixes(g, "W", "Power");
    al("Watt","W"); al("Watt","J/s");
    al("Horsepower","hp");
    fn_pair(g,"Horsepower", Horsepower__to__Watt, "Watt", [](double p){ return p/745.69987; });

    // ─────────────────────────────────────────────────────────────────────────
    // 12. ELECTRICAL
    // ─────────────────────────────────────────────────────────────────────────
    add_node_safe(g,"Volt");    apply_si_prefixes(g,"V", "Voltage");
    add_node_safe(g,"Ampere");  apply_si_prefixes(g,"A", "Current");
    add_node_safe(g,"Ohm");     apply_si_prefixes(g,"\xce\xa9", "Resistance");
    add_node_safe(g,"Siemen");
    add_node_safe(g,"Farad");   apply_si_prefixes(g,"F", "Capacitance");
    add_node_safe(g,"Coulomb");
    add_node_safe(g,"Henry");   apply_si_prefixes(g,"H", "Inductance");

    al("Volt","V"); al("Volt","W/A"); al("Volt","A*ohm");
    al("Ampere","A"); al("Ampere","W/V");
    al("Ohm","ohm"); al("Ohm","\xce\xa9"); al("Ohm","V/A");
    al("Siemen","G"); al("Siemen","\xe2\x84\xa7");
    al("Farad","F"); al("Farad","Q/V");
    al("Coulomb","Q"); al("Coulomb","V*F");
    al("Henry","L"); al("Henry","H");

    // ─────────────────────────────────────────────────────────────────────────
    // 13. PERMEABILITY
    // ─────────────────────────────────────────────────────────────────────────
    add_node_safe(g,"Darcy"); add_node_safe(g,"millidarcy"); add_node_safe(g,"\xc2\xb5m2");
    apply_si_prefixes(g,"D","Permeability");
    al("Darcy","D"); al("millidarcy","mD");
    fn_pair(g,"Darcy",  Darcy__to__um2, "\xc2\xb5m2", [](double d){ return d/0.9869233; });
    fn_pair(g,"Darcy",  [](double d){ return d*1000.0; }, "millidarcy", [](double d){ return d/1000.0; });

    // ─────────────────────────────────────────────────────────────────────────
    // 14. VISCOSITY
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"centipoise","Poise","millipoise","Pascal*second","Reyn","Poiseuille"})
        add_node_safe(g, n);
    apply_si_prefixes(g,"Pa*s","Viscosity");
    // KnotSI on P (no K prefix)
    apply_si_prefixes(g, "P", "Viscosity", false);

    al("centipoise","cP"); al("centipoise","CP");
    al("millipoise","mP");
    al("Poise","P"); al("Poise","g/cm/s");
    al("Pascal*second","Pa*s"); al("Pascal*second","kg/m/s");
    al("Reyn","lbf*s/in2"); al("Reyn","reyn");
    al("Poiseuille","Pl");
    fn_pair(g,"centipoise", centipoise__to__Poise,    "Poise",         [](double v){ return v*100.0; });
    fn_pair(g,"Poise",      Poise__to__Pascal_second, "Pascal*second", [](double v){ return v*10.0; });

    // ─────────────────────────────────────────────────────────────────────────
    // 15. COMPRESSIBILITY
    // ─────────────────────────────────────────────────────────────────────────
    add_node_safe(g,"1/psi"); add_node_safe(g,"1/bar"); add_node_safe(g,"\xc2\xb5sip");
    apply_si_prefixes(g,"sip","Compressibility");
    al("1/psi","1/psia"); al("1/psi","sip");
    al("\xc2\xb5sip","usip");
    al("1/bar","1/bara");
    fn_pair(g,"1/psi", [](double x){ return x*14.50377377322; },
               "1/bar",[](double x){ return x/14.50377377322; });

    // ─────────────────────────────────────────────────────────────────────────
    // 16. VELOCITY
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"kilometer per hour","mile per hour","meter per second"})
        add_node_safe(g, n);
    al("kilometer per hour","kph"); al("kilometer per hour","KPH"); al("kilometer per hour","km/hr");
    al("kilometer per hour","km/h"); al("kilometer per hour","kilometers per hour");
    al("mile per hour","mph"); al("mile per hour","MPH"); al("mile per hour","mi/hr");
    al("mile per hour","miles per hour");
    al("meter per second","m/s"); al("meter per second","m/sec");
    fn_pair(g,"mile per hour",  mile_per_hour__to__kilometer_per_hour,
               "kilometer per hour", [](double v){ return v/1.609344; });
    fn_pair(g,"kilometer per hour", kilometer_per_hour__to__meter_per_second,
               "meter per second",   [](double v){ return v*3.6; });

    // ─────────────────────────────────────────────────────────────────────────
    // 17. DATA
    // ─────────────────────────────────────────────────────────────────────────
    add_node_safe(g,"bit"); add_node_safe(g,"byte");
    apply_data_prefixes_bit(g,  "b");
    apply_data_prefixes_byte(g, "B");
    apply_data_prefixes_bit(g,  "bit");
    apply_data_prefixes_byte(g, "byte");
    al("bit","b"); al("bit","Bit"); al("byte","B"); al("byte","Byte");
    fn_pair(g,"bit", [](double d){ return d/8.0; }, "byte", [](double d){ return d*8.0; });

    // ─────────────────────────────────────────────────────────────────────────
    // 18. RATE
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"stb/day","scf/day","sm3/day","bbl/day","m3/day","ft3/day",
                    "rb/day","rem3/day","litre per minute"})
        add_node_safe(g, n);
    apply_si_prefixes(g,"sm3/day","Rate");
    apply_ogf_prefixes(g,"scf/day");
    apply_ogf_prefixes(g,"stb/day");
    al("stb/day","stbd"); al("scf/day","scfd"); al("sm3/day","sm3d");
    al("bbl/day","bbld"); al("m3/day","m3/d"); al("ft3/day","cf/day");
    al("litre per minute","lpm"); al("litre per minute","l/min");

    // ─────────────────────────────────────────────────────────────────────────
    // 19. DENSITY
    // ─────────────────────────────────────────────────────────────────────────
    for (auto& n : {"g/cm3","kg/m3","lb/ft3","API","SgG","SgW","SgO"})
        add_node_safe(g, n);
    al("g/cm3","g/cc"); al("g/cm3","g/cm^3");
    al("kg/m3","Kg/m3"); al("kg/m3","kg/m^3");
    al("API","degrees"); al("SgG","sgg"); al("SgW","sgw"); al("SgO","sgo");
    fn_pair(g,"g/cm3",  [](double d){ return d*1000.0; }, "kg/m3", [](double d){ return d/1000.0; });
    fn_pair(g,"lb/ft3", [](double d){ return d*16.01846337; }, "kg/m3", [](double d){ return d/16.01846337; });
    fn_pair(g,"API",    [](double d){ return 141.5/(131.5+d); },
               "SgO",   [](double d){ return 141.5/d - 131.5; });

    // ─────────────────────────────────────────────────────────────────────────
    // 20. PRODUCTIVITY INDEX
    // ─────────────────────────────────────────────────────────────────────────
    add_node_safe(g,"stb/day/psi"); add_node_safe(g,"sm3/day/bar"); add_node_safe(g,"sm3/day/kPa");
    al("stb/day/psi","stbd/psi"); al("stb/day/psi","stb/day/psia");
    al("sm3/day/bar","sm3d/bar"); al("sm3/day/bar","sm3/day/bara");
    // stb/day/psi → sm3/day/bar: factor = (sm3/stb) / (bar/psi) = (1/6.289814) × 14.50377 = 2.3059
    fn_pair(g,"stb/day/psi",  [](double d){ return d/6.289814*14.50377377322; },
               "sm3/day/bar", [](double d){ return d*6.289814/14.50377377322; });
    // sm3/day/kPa → sm3/day/bar: 1 bar = 100 kPa, so 1 sm3/day/kPa = 100 sm3/day/bar
    fn_pair(g,"sm3/day/kPa", [](double d){ return d*100.0; },
               "sm3/day/bar", [](double d){ return d/100.0; });

    // ─────────────────────────────────────────────────────────────────────────
    // ADDITIONAL ALIASES — plurals, variant spellings, common abbreviations
    // ─────────────────────────────────────────────────────────────────────────

    // Time plurals and short forms
    al("second",  "seconds");   al("second",  "sec");
    al("minute",  "minutes");   al("minute",  "min"); al("minute","mins");
    al("hour",    "hours");     al("hour",    "hr"); al("hour","hrs");
    al("day",     "days");
    al("week",    "weeks");     al("week",    "w"); al("week","wk"); al("week","wks");
    al("month",   "months");   al("month",   "mo");
    al("year",    "years");     al("year",    "yr"); al("year","yrs");
    al("decade",  "decades");
    al("century", "centuries");
    al("nanosecond",  "nanoseconds");
    al("millisecond", "milliseconds");

    // Spanish time
    al("day",  "d\xc3\xad" "a"); al("day",  "d\xc3\xad" "as");
    al("year", "a\xc3\xb1o"); al("year", "a\xc3\xb1os");
    al("month","mes"); al("month","meses");

    // Weight plurals and extra abbreviations
    al("milligram", "milligrams"); al("milligram", "mgs");
    al("gram",      "grams");
    al("kilogram",  "kilograms"); al("kilogram",  "kgs");
    al("ounce",     "ounces");
    al("pound",     "pounds"); al("pound","lbs");
    al("long ton",  "tons");

    // Volume — decilitre / centilitre aliases
    al("dl","decilitre");  al("dl","decilitres");  al("dl","deciliter");  al("dl","deciliters");
    al("dl","dL");
    al("cl","centilitre"); al("cl","centilitres"); al("cl","centiliter"); al("cl","centiliters");
    al("cl","cL");

    // Volume — oil field
    al("stb","stbl");    al("stb","oil barrel");
    al("Mstb","Mstbl"); al("MMstb","MMstbl"); al("Bstb","Bstbl"); al("Tstb","Tstbl");

    // Volume — standard cubic centimeter (= 1 mL at standard conditions)
    add_node_safe(g, "standard cubic centimeter");
    al("milliliter", "standard cubic centimeter");
    al("milliliter", "standard cubic centimeters");
    al("milliliter", "cc");  // cubic centimeter
    al("milliliter", "mL");

    // Pressure — descriptive aliases
    al("absolute bar",     "abs bar");   al("absolute bar",     "bar absolute");
    al("absolute bar",     "ABS BAR");   al("absolute bar",     "BAR ABSOLUTE");
    al("absolute bar",     "absolute bara");
    al("psia",             "absolute pound/square inch");
    al("psia",             "absolute psia");
    al("psig",             "gauge psi"); al("psig","psi gauge");
    al("barg",             "gauge bar"); al("barg","bar gauge");

    // Temperature — extra aliases for DEGREES variants
    al("Fahrenheit",       "degrees F"); al("Fahrenheit","degrees Fahrenheit");
    al("Kelvin",           "degrees K"); al("Kelvin","degrees Kelvin");
    al("Rankine",          "degrees R"); al("Rankine","degrees Rankine");

    // Area descriptive aliases and compound-notation forms
    al("square meter",     "sqmeter");   al("square meter",     "sq m");
    al("square meter",     "m*m");       al("square meter",     "m3/m");
    al("square kilometer", "sqkm");      al("square kilometer", "sq km");
    al("square mile",      "sqmile");    al("square mile",      "sq mi");
    al("square mile",      "mi*mi");
    al("square foot",      "sqft");      al("square foot",      "sq ft");
    al("square foot",      "ft*ft");     al("square foot",      "ft3/ft");
    al("square inch",      "sqin");      al("square inch",      "sq in");
    al("square yard",      "sqyd");      al("square yard",      "sq yd");
    al("square rod",       "sqrd");      al("square rod",       "sq rd");
    al("square centimeter","sqcm");      al("square centimeter","sq cm");

    // Energy
    al("Joule",  "joule");  al("Joule",  "joules"); al("Joule","J");
    al("calorie","calories");

    // Viscosity
    al("centipoise","cps");

    // Kilogram-mass short form
    al("kilogram mass","kgm");

    // Length plurals
    al("meter",  "meters"); al("meter","metre"); al("meter","metres");
    al("foot",   "feet");
    al("inch",   "inches"); al("inch","in");
    al("yard",   "yards");
    al("mile",   "miles");
    al("kilometer","kilometers"); al("kilometer","kilometres");
    al("centimeter","centimeters"); al("centimeter","centimetres");
    al("millimeter","millimeters"); al("millimeter","millimetres");

    // ─────────────────────────────────────────────────────────────────────────
    // FIX 5: Additional aliases for parity improvement
    // ─────────────────────────────────────────────────────────────────────────

    // Spanish uppercase accented forms
    // DÍA = U+00CD (Í) → bytes D \xc3\x8d A
    al("day",  "D\xc3\x8d" "A");   // DÍA
    al("day",  "D\xc3\x8d" "AS");  // DÍAS
    // AÑO = U+00D1 (Ñ) → bytes A \xc3\x91 O
    al("year", "A\xc3\x91" "O");   // AÑO

    // Gallon variant spellings
    al("gallonUK", "UKgallon");
    al("gallonUS", "USgallon");

    // Volume — cubic plural names
    al("cubic foot",  "cubic feet");
    al("cubic inch",  "cubic inches");

    // Pressure — descriptive and variant names
    al("kPa", "kilopascal"); al("kPa", "kilopascals");
    al("hPa", "hectopascal"); al("hPa", "hectopascals");
    al("kPa", "KPA");  // explicit: CI fails because kPa/KPa both lower to "kpa"
    al("psia", "lb/in2"); al("psia", "lb/in^2");  // lb/in2 = absolute psi, not gauge

    // Compressibility — gauge variants treated as equivalent to absolute
    al("1/psia", "1/psig");
    al("1/bara", "1/barg");

    // Flow/productivity — dash-separator and shortened-day notations
    al("stb/day/psi",  "STB/DAY-PSI");
    al("stb/day/psia", "STB/DAY-PSIA");
    al("sm3/day/bar",  "SM3/DAY-BAR");
    al("sm3/day/bar",  "SM3/DAY-BARA");   // BARA = absolute bar = sm3/day/bar context
    al("sm3/day/kPa",  "SM3/DAY-KPA");
    al("stb/day/psi",  "stb/day-psi");
    al("stb/day/psia", "stb/day-psia");
    al("stb/day/psi",  "stb/d/psi");
    al("stb/day/psia", "stbd/psia");
    al("sm3/day/bar",  "sm3/day-bar");
    al("sm3/day/bar",  "sm3/day-bara");   // dash variant
    al("sm3/day/bar",  "sm3/day/barsa");  // barsa = bara = absolute bar
    al("sm3/day/bar",  "sm3d/bara");
    al("sm3/day/kPa",  "sm3/day-kPa");
    al("sm3/day/kPa",  "sm3d/kPa");
    al("sm3/day/kPa",  "sm3/d/kPa");
    al("sm3/day/bar",  "sm3/d/b");

    // sm3/day variant spellings (stm3 = sm3 in some notations)
    al("sm3d", "stm3d");
    al("sm3d", "stm3/day");

    // Energy — compound-notation equivalents
    al("W*s", "Watt*second");
    al("W*s", "kg*m2/s2");    // 1 J = 1 kg·m²/s² = 1 W·s
    al("kW*h", "kilovatio hora");  // Spanish: kilowatt hour

    // Viscosity — compound-notation equivalent
    al("Pascal*second", "N*s/m2");  // 1 Pa·s = 1 N·s/m²
    al("Dyne", "g*cm/s2");          // 1 dyn = 1 g·cm/s²

    // Area — compound-notation forms
    al("square rod",  "rd2");   al("square rod",  "rd*rd");
    al("square yard", "yd*yd");
    al("square inch", "in*in");

    // ─────────────────────────────────────────────────────────────────────────
    // FIX 6: Comprehensive alias and physics expansion for parity
    // ─────────────────────────────────────────────────────────────────────────

    // === TIME ===
    al("lustrum", "lustrums");
    al("century", "centurys");   // non-standard plural in reference data

    // === AREA (compound notation) ===
    al("square inch", "in3/in");  // in^3/in = in^2 = square inch

    // === VOLUME (compound identity notation) ===
    al("m3",  "m2*m");
    al("cm3", "cm2*cm");
    al("ft3", "ft2*ft");
    al("in3", "in2*in");

    // === OGF volume uppercase aliases (CI fails: prefix ambiguity) ===
    al("Msm3",  "MSM3");
    al("ksm3",  "KSM3");
    al("kstm3", "KSTM3");
    al("Mstm3", "MSTM3");

    // === FLUID VOLUME — US ===
    // oz and fluid ounce are treated 1:1 in Python reference data.
    // Use fn_pair (not al) to avoid corrupting the weight ounce registry path.
    fn_pair(g, "fluid ounce", [](double v){return v;}, "oz", [](double v){return v;});
    al("fluid ounce", "fluid ounces");

    // === GILL, PINT, QUART — abbreviations, plurals, US-named variants ===
    al("gill",  "gi");     al("gill",  "gills");
    al("gill",  "gillUS"); al("gill",  "giUS");
    al("pint",  "pt");     al("pint",  "pints");
    al("pint",  "pintUS"); al("pint",  "ptUS");
    al("quart", "qt");     al("quart", "quarts");
    al("quart", "quartUS"); al("quart", "qtUS");
    al("gallonUK", "gallonUKs");

    // === LITRE/LITER plurals ===
    al("litre",      "litres");
    al("liter",      "liters");
    al("millilitre", "millilitres");

    // === CUBIC VOLUME — hyphenated and non-standard plural forms ===
    al("cubic centimeter", "cubic-centimeter");
    al("cubic centimeter", "cubic centimeters");
    al("cubic meter",      "cubic-meter");
    al("cubic meter",      "cubic meters");
    al("cubic foot",       "cubic-foot");
    al("cubic foot",       "cubic foots");   // non-standard plural in reference data
    al("cubic feet",       "cubic-feet");
    al("cubic inch",       "cubic-inch");
    al("cubic inch",       "cubic inchs");   // non-standard plural
    al("cubic inches",     "cubic-inches");

    // === STANDARD / RESERVOIR VOLUME ===
    al("standard cubic meter",      "scm");
    al("standard cubic meter",      "standard-cubic-meter");
    al("standard cubic meter",      "standard cubic meters");
    al("standard cubic centimeter", "scc");
    al("standard cubic centimeter", "scm3");
    al("standard cubic centimeter", "standard-cubic-centimeter");
    al("reservoir cubic meter",     "reservoir-cubic-meter");
    al("reservoir cubic meter",     "reservoir cubic meters");
    al("standard cubic foot",       "standard-cubic-foot");
    al("standard cubic foot",       "standard cubic foots");  // non-standard plural
    // Reservoir cubic centimeter is not a pre-existing C++ node; create it here.
    add_node_safe(g, "reservoir cubic centimeter");
    al("reservoir cubic centimeter", "recc");
    al("reservoir cubic centimeter", "recm3");
    al("reservoir cubic centimeter", "reservoir-cubic-centimeter");
    al("reservoir cubic centimeter", "reservoir cubic centimeters");

    // === BARREL variants ===
    al("barrel",           "barrels");
    al("reservoir barrel", "reservoir-barrel");
    al("reservoir barrel", "reservoir barrels");
    al("standard barrel",  "standard-barrel");
    al("standard barrel",  "standard barrels");
    al("oil barrel",       "oil-barrel");
    al("oil barrel",       "oil barrels");
    // Oil gallon — isolated node in reference data (no cross-unit conversion)
    add_node_safe(g, "oil gallon");
    al("oil gallon", "oil gallons");

    // scf/day ↔ cf/day: treated as 1:1 in Python reference data
    fn_pair(g, "scf/day", [](double v){return v;}, "cf/day", [](double v){return v;});

    // === PRESSURE — hyphenated forms ===
    al("absolute psi",               "absolute-psi");
    al("absolute pound/square inch", "absolute-pound/square-inch");
    al("psi absolute",               "psi-absolute");
    al("absolute bar",               "absolute-bar");
    al("abs bar",                    "abs-bar");
    al("bar absolute",               "bar-absolute");
    al("millimeters of mercury",     "millimeters-of-mercury");
    al("psi gauge",                  "psi-gauge");
    al("pound/square inch",          "pound/square-inch");
    al("gauge psi",                  "gauge-psi");
    al("bar gauge",                  "bar-gauge");
    al("gauge bar",                  "gauge-bar");

    // === PRESSURE GRADIENT CHAIN ===
    // lb/ft3 ↔ psia/ft: 1 lb/ft³ = 1/144 psi/ft (oilfield gradient convention)
    fn_pair(g, "lb/ft3",
        [](double v){ return v / 144.0; },
        "psia/ft",
        [](double v){ return v * 144.0; });
    // psia/ft ↔ kPa/m: 1 psi/ft = 6.894757 kPa / 0.3048 m = 22.62059 kPa/m
    fn_pair(g, "psia/ft",
        [](double v){ return v * 22.62059; },
        "kPa/m",
        [](double v){ return v / 22.62059; });
    // bara/m ↔ kPa/m: 1 bar = 100 kPa → 1 bar/m = 100 kPa/m
    fn_pair(g, "bara/m",
        [](double v){ return v * 100.0; },
        "kPa/m",
        [](double v){ return v / 100.0; });
    // kPa/m ↔ MPa/km: exactly equal (1 kPa/m = 1000 Pa/m = 1 MPa/km)
    fn_pair(g, "kPa/m",
        [](double v){ return v; },
        "MPa/km",
        [](double v){ return v; });
    // kPa/m ↔ Pa/m: 1 kPa/m = 1000 Pa/m
    fn_pair(g, "kPa/m",
        [](double v){ return v * 1000.0; },
        "Pa/m",
        [](double v){ return v / 1000.0; });

    // === DENSITY — specific gravity connections ===
    // SgO and SgW: numerically equal to g/cc (SG relative to water = 1.0)
    fn_pair(g, "SgO", [](double v){return v;}, "g/cc", [](double v){return v;});
    fn_pair(g, "SgW", [](double v){return v;}, "g/cc", [](double v){return v;});
    // SgG: specific gravity of gas relative to air; 1 SgG = 1.225 kg/m³ (air at STP)
    fn_pair(g, "SgG",
        [](double v){ return v * 1.225; },
        "kg/m3",
        [](double v){ return v / 1.225; });

    // === WEIGHT / MASS — additional aliases ===
    al("metric ton", "metric-ton");
    al("metric ton", "metric tons");
    al("g-mol",  "g-moles");
    al("g-mol",  "g-mols");
    al("Kg-mol", "Kg-moles");
    al("Kg-mol", "Kg-mols");
    al("Kg-mol", "KG-MOL");  // CI fails due to prefix ambiguity; explicit alias needed
    al("grain",       "grains");
    al("pennyweight", "pennyweights");
    al("dram",  "dramch");
    al("dram",  "drams");
    al("stone", "stones");
    al("quarter", "qr");    al("quarter", "qrt");    al("quarter", "quarters");
    al("short hundredweight", "UScwt");
    al("short hundredweight", "short-hundredweight");
    al("short hundredweight", "short hundredweights");
    al("long hundredweight",  "UKcwt");
    al("long hundredweight",  "long-hundredweight");
    al("long hundredweight",  "long hundredweights");
    al("short ton", "short-ton");
    al("short ton", "short tons");
    al("long ton",  "long-ton");
    al("long ton",  "long tons");

    // === FORCE ===
    al("kilogram force", "kilogram-force");

    // === VISCOSITY — Poise ↔ dyne·s/cm² (1 P = 1 dyn·s/cm² by definition) ===
    al("Poise", "dyne*s/cm2");

    // === ENERGY ===
    al("kWh", "KWH");  // CI fails: k prefix ambiguity; explicit alias needed

    // === PRODUCTIVITY — truncated-slash variants in source data ===
    al("stb/day/psi", "STB/DAY/");
    al("sm3/day/bar", "SM3/DAY/");

    // === DENSITY RATIO — lb/stb ===
    // 1 stb = 5.614584 ft³ → 1 lb/stb = 1/5.614584 lb/ft³
    fn_pair(g, "lb/ft3",
        [](double v){ return v * 5.614584; },
        "lb/stb",
        [](double v){ return v / 5.614584; });
    al("lb/stb", "LB/STB");

    // === ENERGY PER RESERVOIR VOLUME ===
    // kJ/rem3: add node; CI handles KJ/rem3 and KJ/REM3 via unique lowercase match
    add_node_safe(g, "kJ/rem3");

    // === MISC TIME-DERIVED UNITS ===
    add_node_safe(g, "sec/day");
    al("sec/day", "sec/d");
    // CI handles SEC/DAY → sec/day and SEC/D → sec/d
    add_node_safe(g, "s2");
    al("s2", "s*s");
    // CI handles S*S → s*s
    add_node_safe(g, "date");
    al("date", "dates");
    // CI handles DATES → dates and DATE → date

    // === UK FLUID VOLUME — abbreviations and plurals ===
    al("fluid ounce UK", "ounceUK");
    al("fluid ounce UK", "fluid ounce UKs");
    al("gillUK",  "giUK");
    al("gillUK",  "gillUKs");
    al("pintUK",  "ptUK");
    al("pintUK",  "pintUKs");
    al("quartUK", "qtUK");
    al("quartUK", "quartUKs");

    // === SPEED — new nodes with physics connections ===
    // ft/sec ↔ m/s: 1 ft/s = 0.3048 m/s
    fn_pair(g, "ft/sec",
        [](double v){ return v * 0.3048; },
        "m/s",
        [](double v){ return v / 0.3048; });
    // km/day ↔ km/h: 1 km/h = 24 km/day
    fn_pair(g, "km/h",
        [](double v){ return v * 24.0; },
        "km/day",
        [](double v){ return v / 24.0; });

    // === TEMPERATURE GRADIENT UNITS ===
    // F/ft ↔ C/m: 1 F/ft = 1/(1.8 × 0.3048) C/m = 1.82269 C/m
    fn_pair(g, "F/ft",
        [](double v){ return v / (1.8 * 0.3048); },
        "C/m",
        [](double v){ return v * (1.8 * 0.3048); });
    // F/ft ↔ F/in: 1 F/ft = 1/12 F/in (1 ft = 12 in)
    fn_pair(g, "F/ft",
        [](double v){ return v / 12.0; },
        "F/in",
        [](double v){ return v * 12.0; });
    // F/ft ↔ F/yd: 1 F/ft = 3 F/yd (1 yd = 3 ft → 1 F/yd = 1/3 F/ft)
    fn_pair(g, "F/ft",
        [](double v){ return v * 3.0; },
        "F/yd",
        [](double v){ return v / 3.0; });
    // C/m ↔ K/m: 1:1 for temperature differences (ΔK = ΔC)
    al("C/m", "K/m");
    // C/m ↔ C/km: 1 C/m = 1000 C/km (1 km = 1000 m)
    fn_pair(g, "C/m",
        [](double v){ return v * 1000.0; },
        "C/km",
        [](double v){ return v / 1000.0; });
    // C/m ↔ C/cm: 1 C/m = 0.01 C/cm (1 m = 100 cm)
    fn_pair(g, "C/m",
        [](double v){ return v * 0.01; },
        "C/cm",
        [](double v){ return v * 100.0; });

    // === TEMPERATURE RATE OF CHANGE UNITS ===
    // C/min ↔ C/hour: 1 C/min = 60 C/hour
    fn_pair(g, "C/min",
        [](double v){ return v * 60.0; },
        "C/hour",
        [](double v){ return v / 60.0; });
    // C/day ↔ C/hour: 1 C/day = 1/24 C/hour
    fn_pair(g, "C/day",
        [](double v){ return v / 24.0; },
        "C/hour",
        [](double v){ return v * 24.0; });
    // C/min ↔ F/min: ΔC × 1.8 = ΔF
    fn_pair(g, "C/min",
        [](double v){ return v * 1.8; },
        "F/min",
        [](double v){ return v / 1.8; });
    // F/min ↔ F/s: 1 F/min = 1/60 F/s
    fn_pair(g, "F/min",
        [](double v){ return v / 60.0; },
        "F/s",
        [](double v){ return v * 60.0; });

} // populate_graph

// ─────────────────────────────────────────────────────────────────────────────
// Singleton graph
// ─────────────────────────────────────────────────────────────────────────────

UDigraph& global_graph() {
    static UDigraph instance;
    static std::once_flag flag;
    std::call_once(flag, [&]() {
        // Pre-load node list and path-memory from previous session (if valid).
        // ConvFn edges are always rebuilt by populate_graph().
        auto cached = load_cache(default_cache_path());
        if (cached) {
            // Move in nodes + path memory; edges are added by populate_graph().
            instance = std::move(*cached);
        }
        populate_graph(instance);
        // Persist the updated cache (grows with each new conversion search).
        try { save_cache(instance, default_cache_path()); } catch (...) {}
    });
    return instance;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

std::vector<std::string> all_unit_names() {
    auto names = global_graph().list_nodes();
    std::sort(names.begin(), names.end());
    return names;
}

bool is_known_unit(const std::string& unit) {
    if (global_graph().has_node(unit)) return true;
    return global_alias_registry().is_known(unit);
}

std::vector<UnitCategory> unit_categories() {
    return {
        {"Length",      {"meter","kilometer","centimeter","millimeter","foot","inch","yard","mile",
                         "nautical mile","thou","tenth","chain","rod","furlong","league",
                         "nautical league","astronomical unit","light year","parsec","scandinavian mile"}},
        {"Area",        {"square meter","square kilometer","square centimeter","square foot",
                         "square inch","square yard","square mile","acre"}},
        {"Volume",      {"cubic meter","litre","cubic foot","cubic inch","cubic yard","gallonUS",
                         "gallonUK","barrel","standard barrel","standard cubic meter",
                         "standard cubic foot","reservoir cubic meter","reservoir barrel"}},
        {"Time",        {"second","millisecond","nanosecond","minute","hour","day","week",
                         "month","year","decade","century","lustrum"}},
        {"Temperature", {"Celsius","Fahrenheit","Kelvin","Rankine"}},
        {"Pressure",    {"Pascal","absolute psi","psi gauge","absolute bar","bar gauge",
                         "atmosphere","Torr","kilogram/square centimeter"}},
        {"Weight",      {"gram","kilogram","milligram","pound","ounce","stone","metric ton",
                         "short ton","long ton","grain"}},
        {"Energy",      {"Joule","Kilojoule","kilowatt hour","British thermal unit",
                         "gram calorie","Watt hour","Watt second"}},
        {"Power",       {"Watt","Horsepower"}},
        {"Force",       {"Newton","kilogram force","Dyne","pound force"}},
        {"Permeability",{"Darcy","millidarcy"}},
        {"Viscosity",   {"centipoise","Poise","Pascal*second"}},
        {"Data",        {"bit","byte"}},
        {"Velocity",    {"kilometer per hour","mile per hour","meter per second"}},
        {"Density",     {"g/cm3","kg/m3","lb/ft3","API","SgG","SgW","SgO"}},
    };
}

} // namespace unyts
