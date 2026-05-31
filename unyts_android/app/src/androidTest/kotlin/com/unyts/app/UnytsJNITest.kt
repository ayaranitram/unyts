package com.unyts.app

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import com.unyts.app.jni.UnytsJNI
import kotlin.math.abs

@RunWith(AndroidJUnit4::class)
class UnytsJNITest {

    init {
        UnytsJNI.nativeInit()
    }

    @Test
    fun nativeInit_succeeds() {
        // Covered implicitly by all tests below.
    }

    @Test
    fun convert_meter_to_foot() {
        val result = UnytsJNI.nativeConvert(1.0, "meter", "foot")
        assertFalse("Should not be NaN", result.isNaN())
        assertTrue("1 m ≈ 3.28084 ft", abs(result - 3.28084) < 0.001)
    }

    @Test
    fun convert_unknown_returns_nan() {
        val result = UnytsJNI.nativeConvert(1.0, "blah", "foot")
        assertTrue("Unknown unit should return NaN", result.isNaN())
    }

    @Test
    fun convertible_meter_foot_is_true() {
        assertTrue(UnytsJNI.nativeConvertible("meter", "foot"))
    }

    @Test
    fun convertible_meter_second_is_false() {
        assertFalse(UnytsJNI.nativeConvertible("meter", "second"))
    }

    @Test
    fun allUnits_returns_many_units() {
        val units = UnytsJNI.nativeAllUnits()
        assertTrue("Expected >1000 units, got ${units.size}", units.size > 1000)
    }

    @Test
    fun isKnownUnit_meter_is_true() {
        assertTrue(UnytsJNI.nativeIsKnownUnit("meter"))
    }

    @Test
    fun isKnownUnit_nonsense_is_false() {
        assertFalse(UnytsJNI.nativeIsKnownUnit("not_a_real_unit_xyz"))
    }

    @Test
    fun fvf_roundtrip() {
        UnytsJNI.nativeSetFvf(1.5)
        assertEquals(1.5, UnytsJNI.nativeGetFvf(), 1e-9)
        UnytsJNI.nativeSetFvf(1.0) // restore default
    }

    @Test
    fun timeout_roundtrip() {
        UnytsJNI.nativeSetTimeoutMs(3000)
        assertEquals(3000, UnytsJNI.nativeGetTimeoutMs())
        UnytsJNI.nativeSetTimeoutMs(5000) // restore default
    }

    @Test
    fun version_is_not_empty() {
        val v = UnytsJNI.nativeVersion()
        assertTrue("Version should not be empty", v.isNotEmpty())
    }
}
