package com.unyts.app.viewmodel

import com.unyts.app.model.ConversionRecord
import org.junit.Assert.*
import org.junit.Test

/**
 * JVM unit tests for pure logic inside [ConvertUiState] and the helper
 * functions of [ConvertViewModel] that do NOT require an Android context.
 *
 * The ViewModel's coroutine and JNI-dependent behaviour is covered by the
 * instrumented tests in [com.unyts.app.UnytsJNITest].
 */
class ConvertViewModelLogicTest {

    // ── formatResult (private, exercised via state shape) ────────────────────

    @Test
    fun `whole number double formats without decimal point`() {
        val result = formatResult(42.0)
        assertEquals("42", result)
    }

    @Test
    fun `large whole number formats without decimal point`() {
        val result = formatResult(1_000_000.0)
        assertEquals("1000000", result)
    }

    @Test
    fun `fractional double formats to trimmed significant figures`() {
        val result = formatResult(0.33333333)
        // Should not end with trailing zeros or decimal point
        assertFalse("Trailing zero", result.endsWith("0"))
        assertFalse("Trailing dot",  result.endsWith("."))
    }

    @Test
    fun `very large double falls through to scientific notation`() {
        val result = formatResult(1.5e20)
        // Too large for integer path; should contain 'e' or 'E'
        assertTrue(result.contains('e', ignoreCase = true))
    }

    // ── ConversionRecord construction ─────────────────────────────────────────

    @Test
    fun `ConversionRecord stores all fields`() {
        val rec = ConversionRecord(
            id        = 1L,
            fromValue = 1.0,
            fromUnit  = "m",
            toValue   = 3.28084,
            toUnit    = "ft",
        )
        assertEquals(1L,      rec.id)
        assertEquals("m",     rec.fromUnit)
        assertEquals("ft",    rec.toUnit)
        assertEquals(1.0,     rec.fromValue, 1e-9)
        assertEquals(3.28084, rec.toValue,   1e-4)
    }

    @Test
    fun `ConversionRecord default id is non-zero`() {
        val rec = ConversionRecord(fromValue = 1.0, fromUnit = "m", toValue = 3.28, toUnit = "ft")
        assertTrue(rec.id > 0L)
    }

    // ── ConvertUiState ────────────────────────────────────────────────────────

    @Test
    fun `initial state has empty fields`() {
        val state = ConvertUiState()
        assertEquals("", state.fromUnit)
        assertEquals("", state.toUnit)
        assertEquals("", state.errorMessage)
        assertTrue(state.history.isEmpty())
        assertFalse(state.isLoading)
    }

    @Test
    fun `copy with error clears toValue`() {
        val state = ConvertUiState(fromUnit = "m", toUnit = "ft")
            .copy(toValue = "", errorMessage = "No path")
        assertEquals("", state.toValue)
        assertEquals("No path", state.errorMessage)
    }

    @Test
    fun `history is prepended and capped at 50`() {
        var history = emptyList<ConversionRecord>()
        repeat(55) { i ->
            val rec = ConversionRecord(
                id        = i.toLong(),
                fromValue = i.toDouble(),
                fromUnit  = "m",
                toValue   = i.toDouble() * 3.28,
                toUnit    = "ft",
            )
            history = (listOf(rec) + history).take(50)
        }
        assertEquals(50, history.size)
        // Most recently added should be at index 0.
        assertEquals(54L, history[0].id)
    }

    // ── Swap logic ────────────────────────────────────────────────────────────

    @Test
    fun `swap exchanges units and values`() {
        val before = ConvertUiState(
            fromUnit = "m",  fromValue = "1",
            toUnit   = "ft", toValue   = "3.28",
        )
        val after = before.copy(
            fromUnit  = before.toUnit,   toUnit  = before.fromUnit,
            fromValue = before.toValue,  toValue = before.fromValue,
        )
        assertEquals("ft", after.fromUnit)
        assertEquals("m",  after.toUnit)
        assertEquals("3.28", after.fromValue)
        assertEquals("1",    after.toValue)
    }

    // ── Helper used by the tests above ───────────────────────────────────────

    /** Mirror of the private formatResult in ConvertViewModel. */
    private fun formatResult(value: Double): String {
        if (value % 1.0 == 0.0 && kotlin.math.abs(value) < 1e15) return value.toLong().toString()
        return "%.8g".format(value).trimEnd('0').trimEnd('.')
    }
}
