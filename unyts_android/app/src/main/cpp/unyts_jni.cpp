// unyts_jni.cpp — JNI bridge between Android (Kotlin) and the unyts C++ core.
//
// All entry points delegate to the pure-C API (unyts_capi.h).  A singleton
// UnytsContext is created on nativeInit() and lives for the process lifetime.

#include <jni.h>
#include <android/log.h>
#include <cstring>
#include <cmath>
#include <limits>
#include <vector>
#include <string>

#include "unyts/unyts_capi.h"

#define LOG_TAG "UnytsJNI"
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

static UnytsContext* g_ctx = nullptr;

// Convenience: return NaN to signal a failed conversion to Kotlin.
static constexpr double NaN = std::numeric_limits<double>::quiet_NaN();

extern "C" {

// ── Lifecycle ─────────────────────────────────────────────────────────────────

JNIEXPORT void JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeInit(JNIEnv*, jobject)
{
    if (!g_ctx) {
        g_ctx = unyts_create();
        LOGD("unyts context created, %d units loaded", unyts_unit_count(g_ctx));
    }
}

JNIEXPORT void JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeDestroy(JNIEnv*, jobject)
{
    if (g_ctx) {
        unyts_destroy(g_ctx);
        g_ctx = nullptr;
    }
}

// ── Conversion ────────────────────────────────────────────────────────────────

JNIEXPORT jdouble JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeConvert(
        JNIEnv* env, jobject,
        jdouble value, jstring fromUnit, jstring toUnit)
{
    if (!g_ctx) return NaN;
    const char* from = env->GetStringUTFChars(fromUnit, nullptr);
    const char* to   = env->GetStringUTFChars(toUnit,   nullptr);
    double out = 0.0;
    int rc = unyts_convert(g_ctx, (double)value, from, to, &out);
    env->ReleaseStringUTFChars(fromUnit, from);
    env->ReleaseStringUTFChars(toUnit,   to);
    if (rc != UNYTS_OK) { LOGD("convert failed rc=%d", rc); return NaN; }
    return (jdouble)out;
}

JNIEXPORT jboolean JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeConvertible(
        JNIEnv* env, jobject, jstring fromUnit, jstring toUnit)
{
    if (!g_ctx) return JNI_FALSE;
    const char* from = env->GetStringUTFChars(fromUnit, nullptr);
    const char* to   = env->GetStringUTFChars(toUnit,   nullptr);
    int rc = unyts_convertible(g_ctx, from, to);
    env->ReleaseStringUTFChars(fromUnit, from);
    env->ReleaseStringUTFChars(toUnit,   to);
    return (jboolean)(rc == 1);
}

JNIEXPORT jdouble JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeConversionFactor(
        JNIEnv* env, jobject, jstring fromUnit, jstring toUnit)
{
    if (!g_ctx) return NaN;
    const char* from = env->GetStringUTFChars(fromUnit, nullptr);
    const char* to   = env->GetStringUTFChars(toUnit,   nullptr);
    double factor = 0.0;
    int rc = unyts_conversion_factor(g_ctx, from, to, &factor);
    env->ReleaseStringUTFChars(fromUnit, from);
    env->ReleaseStringUTFChars(toUnit,   to);
    return (rc == UNYTS_OK) ? (jdouble)factor : NaN;
}

// ── Unit discovery ────────────────────────────────────────────────────────────

JNIEXPORT jobjectArray JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeAllUnits(JNIEnv* env, jobject)
{
    jclass stringClass = env->FindClass("java/lang/String");
    if (!g_ctx) return env->NewObjectArray(0, stringClass, nullptr);

    // 1 MB buffer — enough for ~1700 unit names.
    const int BUF = 1 << 20;
    std::vector<char> buf(BUF);
    unyts_all_units(g_ctx, buf.data(), BUF);

    // Split newline-delimited string into individual unit name tokens.
    std::vector<std::string> units;
    units.reserve(2048);
    char* ptr = buf.data();
    char* end = ptr + std::strlen(ptr);
    while (ptr < end) {
        char* nl  = static_cast<char*>(std::memchr(ptr, '\n', end - ptr));
        size_t len = nl ? static_cast<size_t>(nl - ptr) : static_cast<size_t>(end - ptr);
        if (len > 0) units.emplace_back(ptr, len);
        if (!nl) break;
        ptr = nl + 1;
    }

    jobjectArray arr = env->NewObjectArray(static_cast<jsize>(units.size()), stringClass, nullptr);
    for (jsize i = 0; i < static_cast<jsize>(units.size()); ++i) {
        jstring s = env->NewStringUTF(units[i].c_str());
        env->SetObjectArrayElement(arr, i, s);
        env->DeleteLocalRef(s);
    }
    return arr;
}

JNIEXPORT jboolean JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeIsKnownUnit(
        JNIEnv* env, jobject, jstring unitName)
{
    if (!g_ctx) return JNI_FALSE;
    const char* name = env->GetStringUTFChars(unitName, nullptr);
    int rc = unyts_is_known_unit(g_ctx, name);
    env->ReleaseStringUTFChars(unitName, name);
    return (jboolean)(rc == 1);
}

// ── Context configuration ─────────────────────────────────────────────────────

JNIEXPORT void JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeSetFvf(JNIEnv*, jobject, jdouble fvf)
{
    if (g_ctx) unyts_set_fvf(g_ctx, (double)fvf);
}

JNIEXPORT jdouble JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeGetFvf(JNIEnv*, jobject)
{
    return g_ctx ? (jdouble)unyts_get_fvf(g_ctx) : 1.0;
}

JNIEXPORT void JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeSetTimeoutMs(JNIEnv*, jobject, jint ms)
{
    if (g_ctx) unyts_set_timeout_ms(g_ctx, (int)ms);
}

JNIEXPORT jint JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeGetTimeoutMs(JNIEnv*, jobject)
{
    return g_ctx ? (jint)unyts_get_timeout_ms(g_ctx) : 5000;
}

JNIEXPORT jstring JNICALL
Java_com_unyts_app_jni_UnytsJNI_nativeVersion(JNIEnv* env, jobject)
{
    return env->NewStringUTF(unyts_version());
}

} // extern "C"
