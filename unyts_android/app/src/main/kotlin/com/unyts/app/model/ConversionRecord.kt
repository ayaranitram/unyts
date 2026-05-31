package com.unyts.app.model

/**
 * A single completed conversion kept in the in-memory history list.
 *
 * [id] is the system epoch-millis at the time of the conversion; used as a
 * stable list key for Compose.
 */
data class ConversionRecord(
    val id:        Long   = System.currentTimeMillis(),
    val fromValue: Double,
    val fromUnit:  String,
    val toValue:   Double,
    val toUnit:    String,
)
