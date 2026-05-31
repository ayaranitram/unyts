/**
 * unyts_capi.h — Pure-C public API for the unyts unit conversion library.
 *
 * This header is intentionally plain C (no C++ types, no name mangling) so
 * that the shared library (unyts_capi.dll / libunyts_capi.so) can be loaded
 * via FFI from any language: Python ctypes, Swift, Kotlin JNI, C, etc.
 *
 * All string buffers are caller-allocated.  Every function that writes into
 * a buffer requires the caller to pass the buffer's capacity (in bytes); the
 * library never writes past that boundary.
 *
 * Return codes
 * ────────────
 *   UNYTS_OK             (0) — success
 *   UNYTS_ERR_NO_PATH   (-1) — no conversion path found between the two units
 *   UNYTS_ERR_BADARG    (-2) — null pointer or empty unit string supplied
 *   UNYTS_ERR_OVERFLOW  (-3) — the output buffer was too small; result truncated
 */

#ifndef UNYTS_CAPI_H
#define UNYTS_CAPI_H

#ifdef __cplusplus
extern "C" {
#endif

/* ── DLL import/export macro ─────────────────────────────────────────────── */
#if defined(_WIN32) || defined(_WIN64)
#  if defined(UNYTS_CAPI_BUILDING_DLL)
#    define UNYTS_API __declspec(dllexport)
#  else
#    define UNYTS_API __declspec(dllimport)
#  endif
#else
#  define UNYTS_API __attribute__((visibility("default")))
#endif

/* ── Return codes ────────────────────────────────────────────────────────── */
#define UNYTS_OK            0
#define UNYTS_ERR_NO_PATH  (-1)
#define UNYTS_ERR_BADARG   (-2)
#define UNYTS_ERR_OVERFLOW (-3)

/* ── Opaque context ──────────────────────────────────────────────────────── */

/**
 * Opaque handle to a unyts conversion context.
 *
 * The context currently wraps the global singleton graph but is exposed as
 * an opaque pointer to keep the API stable if per-context state is added
 * later (e.g. per-context FVF, timeout, or loaded parameter file).
 */
typedef struct UnytsContext UnytsContext;

/* ── Lifecycle ───────────────────────────────────────────────────────────── */

/**
 * Create and initialise a unyts context.
 *
 * The first call triggers graph construction (O(1 s) on first build, cached
 * on subsequent calls within the same process).  Returns NULL on allocation
 * failure (extremely unlikely on any modern OS).
 */
UNYTS_API UnytsContext* unyts_create(void);

/**
 * Destroy a context previously returned by unyts_create().
 * Passing NULL is a no-op.
 */
UNYTS_API void unyts_destroy(UnytsContext* ctx);

/* ── Core conversion ─────────────────────────────────────────────────────── */

/**
 * Convert `value` from `from_unit` to `to_unit`.
 *
 * @param ctx        Initialised context.
 * @param value      Input numeric value.
 * @param from_unit  Source unit name or alias (null-terminated UTF-8).
 * @param to_unit    Target unit name or alias (null-terminated UTF-8).
 * @param out_value  Receives the converted value on success; unchanged on error.
 *
 * @return UNYTS_OK on success, UNYTS_ERR_NO_PATH if no path exists,
 *         UNYTS_ERR_BADARG for null/empty arguments.
 */
UNYTS_API int unyts_convert(UnytsContext* ctx,
                             double        value,
                             const char*   from_unit,
                             const char*   to_unit,
                             double*       out_value);

/**
 * Test whether a conversion path exists between two units.
 *
 * @return 1 if convertible, 0 if not, UNYTS_ERR_BADARG on bad arguments.
 */
UNYTS_API int unyts_convertible(UnytsContext* ctx,
                                 const char*   from_unit,
                                 const char*   to_unit);

/**
 * Return the scalar factor such that: `result = value * factor`.
 * Equivalent to unyts_convert(ctx, 1.0, from, to, &factor).
 */
UNYTS_API int unyts_conversion_factor(UnytsContext* ctx,
                                       const char*   from_unit,
                                       const char*   to_unit,
                                       double*       out_factor);

/* ── Unit discovery ──────────────────────────────────────────────────────── */

/**
 * Write a newline-separated list of all known unit names into `out_buf`.
 *
 * @param ctx         Initialised context.
 * @param out_buf     Caller-allocated buffer to receive the list.
 * @param buf_len     Capacity of `out_buf` in bytes (including null terminator).
 *
 * @return UNYTS_OK on success, UNYTS_ERR_OVERFLOW if the buffer was too small
 *         (the string is still null-terminated and contains as many complete
 *         lines as fit).
 */
UNYTS_API int unyts_all_units(UnytsContext* ctx,
                               char*         out_buf,
                               int           buf_len);

/**
 * Return the number of units known to the engine (useful for sizing buffers).
 */
UNYTS_API int unyts_unit_count(UnytsContext* ctx);

/**
 * Test whether `unit_name` is a known unit or alias.
 * @return 1 if known, 0 if unknown, UNYTS_ERR_BADARG on null argument.
 */
UNYTS_API int unyts_is_known_unit(UnytsContext* ctx, const char* unit_name);

/* ── Context configuration ───────────────────────────────────────────────── */

/**
 * Set the formation-volume-factor used in FVF conversions (default 1.0).
 * This mirrors unyts_parameters.fvf in the Python API.
 */
UNYTS_API void   unyts_set_fvf(UnytsContext* ctx, double fvf);
UNYTS_API double unyts_get_fvf(UnytsContext* ctx);

/**
 * Set the BFS/DFS search timeout in milliseconds (default 5000 ms).
 */
UNYTS_API void unyts_set_timeout_ms(UnytsContext* ctx, int timeout_ms);
UNYTS_API int  unyts_get_timeout_ms(UnytsContext* ctx);

/* ── Library version ─────────────────────────────────────────────────────── */

/** Return a null-terminated version string, e.g. "0.1.0". */
UNYTS_API const char* unyts_version(void);

#ifdef __cplusplus
} // extern "C"
#endif

#endif /* UNYTS_CAPI_H */
