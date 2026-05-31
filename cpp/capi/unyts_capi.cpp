// capi/unyts_capi.cpp — Implementation of the pure-C public API.
//
// Each UnytsContext wraps per-context state (FVF, timeout) on top of the
// global graph/registry singleton that is shared across all contexts in the
// same process.  Graph initialisation is therefore performed only once.
//
// Build note: UNYTS_CAPI_BUILDING_DLL is supplied via CMake so that
// UNYTS_API expands to __declspec(dllexport) on Windows.

#include "unyts/unyts_capi.h"
#include "unyts/converter.hpp"
#include "unyts/database.hpp"

#include <algorithm>
#include <cstring>
#include <string>
#include <vector>

// ─────────────────────────────────────────────────────────────────────────────
// Internal context definition
// ─────────────────────────────────────────────────────────────────────────────

struct UnytsContext {
    double fvf        = 1.0;
    int    timeout_ms = 5000;
};

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

static inline bool bad_string(const char* s) {
    return s == nullptr || s[0] == '\0';
}

// ─────────────────────────────────────────────────────────────────────────────
// Lifecycle
// ─────────────────────────────────────────────────────────────────────────────

extern "C" {

UNYTS_API UnytsContext* unyts_create(void)
{
    // Ensure the global graph singleton is initialised.
    unyts::global_graph();
    return new (std::nothrow) UnytsContext{};
}

UNYTS_API void unyts_destroy(UnytsContext* ctx)
{
    delete ctx;
}

// ─────────────────────────────────────────────────────────────────────────────
// Core conversion
// ─────────────────────────────────────────────────────────────────────────────

UNYTS_API int unyts_convert(UnytsContext* ctx,
                             double        value,
                             const char*   from_unit,
                             const char*   to_unit,
                             double*       out_value)
{
    if (ctx == nullptr || bad_string(from_unit) || bad_string(to_unit) || out_value == nullptr)
        return UNYTS_ERR_BADARG;

    // Apply context timeout for this call.
    int prev_timeout = unyts::get_search_timeout_ms();
    unyts::set_search_timeout_ms(ctx->timeout_ms);

    auto result = unyts::convert(value, std::string(from_unit), std::string(to_unit));

    unyts::set_search_timeout_ms(prev_timeout);

    if (!result)
        return UNYTS_ERR_NO_PATH;

    *out_value = result->value;
    return UNYTS_OK;
}

UNYTS_API int unyts_convertible(UnytsContext* ctx,
                                 const char*   from_unit,
                                 const char*   to_unit)
{
    if (ctx == nullptr || bad_string(from_unit) || bad_string(to_unit))
        return UNYTS_ERR_BADARG;

    return unyts::convertible(std::string(from_unit), std::string(to_unit)) ? 1 : 0;
}

UNYTS_API int unyts_conversion_factor(UnytsContext* ctx,
                                       const char*   from_unit,
                                       const char*   to_unit,
                                       double*       out_factor)
{
    if (ctx == nullptr || bad_string(from_unit) || bad_string(to_unit) || out_factor == nullptr)
        return UNYTS_ERR_BADARG;

    auto f = unyts::conversion_factor(std::string(from_unit), std::string(to_unit));
    if (!f)
        return UNYTS_ERR_NO_PATH;

    *out_factor = *f;
    return UNYTS_OK;
}

// ─────────────────────────────────────────────────────────────────────────────
// Unit discovery
// ─────────────────────────────────────────────────────────────────────────────

UNYTS_API int unyts_all_units(UnytsContext* ctx,
                               char*         out_buf,
                               int           buf_len)
{
    if (ctx == nullptr || out_buf == nullptr || buf_len <= 0)
        return UNYTS_ERR_BADARG;

    const auto& names = unyts::all_unit_names();

    int pos     = 0;
    int rc      = UNYTS_OK;
    for (const auto& name : names) {
        int needed = static_cast<int>(name.size()) + 1; // name + '\n'
        if (pos + needed >= buf_len) {
            rc = UNYTS_ERR_OVERFLOW;
            break;
        }
        std::memcpy(out_buf + pos, name.c_str(), name.size());
        pos += static_cast<int>(name.size());
        out_buf[pos++] = '\n';
    }
    // Always null-terminate.
    out_buf[pos] = '\0';
    return rc;
}

UNYTS_API int unyts_unit_count(UnytsContext* ctx)
{
    if (ctx == nullptr)
        return UNYTS_ERR_BADARG;
    return static_cast<int>(unyts::all_unit_names().size());
}

UNYTS_API int unyts_is_known_unit(UnytsContext* ctx, const char* unit_name)
{
    if (ctx == nullptr || unit_name == nullptr)
        return UNYTS_ERR_BADARG;
    return unyts::is_known_unit(std::string(unit_name)) ? 1 : 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// Context configuration
// ─────────────────────────────────────────────────────────────────────────────

UNYTS_API void unyts_set_fvf(UnytsContext* ctx, double fvf)
{
    if (ctx) ctx->fvf = fvf;
}

UNYTS_API double unyts_get_fvf(UnytsContext* ctx)
{
    return ctx ? ctx->fvf : 1.0;
}

UNYTS_API void unyts_set_timeout_ms(UnytsContext* ctx, int timeout_ms)
{
    if (ctx) ctx->timeout_ms = timeout_ms;
}

UNYTS_API int unyts_get_timeout_ms(UnytsContext* ctx)
{
    return ctx ? ctx->timeout_ms : 5000;
}

// ─────────────────────────────────────────────────────────────────────────────
// Version
// ─────────────────────────────────────────────────────────────────────────────

UNYTS_API const char* unyts_version(void)
{
    return "0.1.0";
}

} // extern "C"
