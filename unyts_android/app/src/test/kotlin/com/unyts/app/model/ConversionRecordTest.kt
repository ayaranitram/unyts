package com.unyts.app.model

import org.junit.Assert.*
import org.junit.Test

class ConversionRecordTest {

    @Test
    fun `equality and copy work correctly`() {
        val r1 = ConversionRecord(1L, 1.0, "m", 3.28084, "ft")
        val r2 = r1.copy(toUnit = "inch")
        assertNotEquals(r1, r2)
        assertEquals("inch", r2.toUnit)
        assertEquals(r1.fromValue, r2.fromValue, 1e-9)
    }

    @Test
    fun `two records with different ids are not equal`() {
        val r1 = ConversionRecord(1L, 1.0, "kg", 2.20462, "lb")
        val r2 = ConversionRecord(2L, 1.0, "kg", 2.20462, "lb")
        assertNotEquals(r1, r2)
    }
}
