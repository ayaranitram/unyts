/**
 * capi/test_capi.c — Smoke-test for the unyts C API (plain C, no C++).
 *
 * Build:  cl /nologo /I../include test_capi.c unyts_capi.lib
 * Run:    test_capi.exe  (unyts_capi.dll must be on PATH)
 */

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "unyts/unyts_capi.h"

#define PASS "\033[32mPASS\033[0m"
#define FAIL "\033[31mFAIL\033[0m"

static int n_pass = 0, n_fail = 0;

static void check(const char* desc, int cond) {
    if (cond) { printf("  %s  %s\n", PASS, desc); ++n_pass; }
    else       { printf("  %s  %s\n", FAIL, desc); ++n_fail; }
}

static void check_near(const char* desc, double got, double expected, double tol) {
    double diff = got - expected;
    if (diff < 0) diff = -diff;
    int ok = (diff <= tol * (expected < 0 ? -expected : expected) + 1e-12);
    if (ok) { printf("  %s  %s  (%.6g)\n", PASS, desc, got); ++n_pass; }
    else    { printf("  %s  %s  (got %.6g, expected %.6g)\n", FAIL, desc, got, expected); ++n_fail; }
}

int main(void) {
    printf("unyts C API smoke-test  v%s\n", unyts_version());
    printf("─────────────────────────────────────────────\n");

    /* ── Lifecycle ────────────────────────────────────────────────────── */
    UnytsContext* ctx = unyts_create();
    check("unyts_create() returns non-NULL", ctx != NULL);

    /* ── Unit count ──────────────────────────────────────────────────── */
    int n = unyts_unit_count(ctx);
    check("unyts_unit_count() > 1000", n > 1000);
    printf("       (%d units registered)\n", n);

    /* ── is_known_unit ───────────────────────────────────────────────── */
    check("'meter' is known",    unyts_is_known_unit(ctx, "meter")    == 1);
    check("'kg' is known",       unyts_is_known_unit(ctx, "kg")       == 1);
    check("'xyzzy' is unknown",  unyts_is_known_unit(ctx, "xyzzy")    == 0);

    /* ── convertible ─────────────────────────────────────────────────── */
    check("meter→foot: convertible",   unyts_convertible(ctx, "meter",    "foot")   == 1);
    check("kg→lb: convertible",        unyts_convertible(ctx, "kg",       "lb")     == 1);
    check("meter→kg: not convertible", unyts_convertible(ctx, "meter",    "kg")     == 0);

    /* ── convert ─────────────────────────────────────────────────────── */
    double v = 0.0;
    int rc;

    rc = unyts_convert(ctx, 1.0, "km", "m", &v);
    check("unyts_convert returns OK", rc == UNYTS_OK);
    check_near("1 km → m = 1000", v, 1000.0, 1e-6);

    rc = unyts_convert(ctx, 1.0, "m", "ft", &v);
    check_near("1 m → ft = 3.28084", v, 3.28084, 1e-4);

    rc = unyts_convert(ctx, 212.0, "F", "C", &v);
    check_near("212 F → C = 100", v, 100.0, 1e-6);

    rc = unyts_convert(ctx, 1.0, "bara", "psia", &v);
    check_near("1 bara → psia ≈ 14.5038", v, 14.5038, 1e-4);

    rc = unyts_convert(ctx, 1.0, "stb", "m3", &v);
    check_near("1 stb → m3 ≈ 0.158987", v, 0.158987, 1e-4);

    /* ── No-path case ─────────────────────────────────────────────────── */
    rc = unyts_convert(ctx, 1.0, "meter", "kilogram", &v);
    check("meter→kilogram returns UNYTS_ERR_NO_PATH", rc == UNYTS_ERR_NO_PATH);

    /* ── Bad-arg cases ───────────────────────────────────────────────── */
    rc = unyts_convert(ctx, 1.0, NULL, "m", &v);
    check("NULL from_unit returns UNYTS_ERR_BADARG", rc == UNYTS_ERR_BADARG);
    rc = unyts_convert(ctx, 1.0, "m", "", &v);
    check("empty to_unit returns UNYTS_ERR_BADARG",  rc == UNYTS_ERR_BADARG);

    /* ── conversion_factor ───────────────────────────────────────────── */
    double f = 0.0;
    rc = unyts_conversion_factor(ctx, "kg", "lb", &f);
    check("conversion_factor OK", rc == UNYTS_OK);
    check_near("kg→lb factor ≈ 2.2046", f, 2.2046, 1e-3);

    /* ── Context config ──────────────────────────────────────────────── */
    unyts_set_fvf(ctx, 1.05);
    check("set/get FVF", unyts_get_fvf(ctx) == 1.05);
    unyts_set_timeout_ms(ctx, 3000);
    check("set/get timeout", unyts_get_timeout_ms(ctx) == 3000);

    /* ── all_units (truncated) ───────────────────────────────────────── */
    char buf[256];
    /* Small buffer → expect UNYTS_ERR_OVERFLOW, still null-terminated */
    rc = unyts_all_units(ctx, buf, (int)sizeof(buf));
    check("all_units with small buf returns UNYTS_ERR_OVERFLOW",
          rc == UNYTS_ERR_OVERFLOW);
    check("all_units output is null-terminated", buf[sizeof(buf)-1] == '\0' || buf[0] != '\0');

    /* Large buffer → expect UNYTS_OK */
    int big = (n + 1) * 32;
    char* bigbuf = (char*)malloc((size_t)big);
    if (bigbuf) {
        rc = unyts_all_units(ctx, bigbuf, big);
        check("all_units with large buf returns UNYTS_OK", rc == UNYTS_OK);
        free(bigbuf);
    }

    /* ── Cleanup ─────────────────────────────────────────────────────── */
    unyts_destroy(ctx);
    unyts_destroy(NULL);   /* must not crash */
    check("unyts_destroy(NULL) does not crash", 1);

    /* ── Summary ─────────────────────────────────────────────────────── */
    printf("─────────────────────────────────────────────\n");
    printf("Result: %d passed, %d failed\n", n_pass, n_fail);
    return n_fail == 0 ? 0 : 1;
}
