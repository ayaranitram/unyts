package com.unyts.app.jni

/**
 * Thin Kotlin object that declares all `external` functions mapping 1:1 to
 * the native entry points in unyts_jni.cpp.
 *
 * Prefer [UnytsService] for a coroutine-safe, settings-aware API.
 */
object UnytsJNI {

    init {
        System.loadLibrary("unyts_jni")
    }

    external fun nativeInit()
    external fun nativeDestroy()

    /** Returns the converted value, or NaN if no conversion path exists. */
    external fun nativeConvert(value: Double, fromUnit: String, toUnit: String): Double

    external fun nativeConvertible(fromUnit: String, toUnit: String): Boolean
    external fun nativeConversionFactor(fromUnit: String, toUnit: String): Double

    external fun nativeAllUnits(): Array<String>
    external fun nativeIsKnownUnit(unitName: String): Boolean

    external fun nativeSetFvf(fvf: Double)
    external fun nativeGetFvf(): Double
    external fun nativeSetTimeoutMs(ms: Int)
    external fun nativeGetTimeoutMs(): Int

    external fun nativeVersion(): String
}
