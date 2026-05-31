package com.unyts.app.jni

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.doublePreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "unyts_settings")

/**
 * Coroutine-safe wrapper around [UnytsJNI] with DataStore-backed settings.
 *
 * One instance should live in the Application (e.g. injected into the ViewModel
 * via [AndroidViewModel]).  The underlying native context is a singleton whose
 * lifetime equals the process lifetime.
 */
class UnytsService(private val context: Context) {

    companion object {
        private val KEY_FVF        = doublePreferencesKey("fvf")
        private val KEY_TIMEOUT_MS = intPreferencesKey("timeout_ms")
    }

    init {
        UnytsJNI.nativeInit()
    }

    /** All known unit names, sorted and cached after the first access. */
    val allUnits: List<String> by lazy {
        UnytsJNI.nativeAllUnits().toList().sorted()
    }

    val version: String get() = UnytsJNI.nativeVersion()

    // ── Conversion ────────────────────────────────────────────────────────────

    /**
     * Convert [value] from [from] to [to] on [Dispatchers.Default].
     * Returns [Result.success] with the converted Double, or [Result.failure]
     * if no conversion path exists.
     */
    suspend fun convert(value: Double, from: String, to: String): Result<Double> =
        withContext(Dispatchers.Default) {
            runCatching {
                val result = UnytsJNI.nativeConvert(value, from, to)
                if (result.isNaN()) error("No conversion path: $from → $to")
                result
            }
        }

    fun isConvertible(from: String, to: String): Boolean =
        UnytsJNI.nativeConvertible(from, to)

    fun isKnownUnit(unit: String): Boolean =
        UnytsJNI.nativeIsKnownUnit(unit)

    // ── Settings ──────────────────────────────────────────────────────────────

    fun setFvf(fvf: Double)       = UnytsJNI.nativeSetFvf(fvf)
    fun getFvf(): Double          = UnytsJNI.nativeGetFvf()
    fun setTimeoutMs(ms: Int)     = UnytsJNI.nativeSetTimeoutMs(ms)
    fun getTimeoutMs(): Int       = UnytsJNI.nativeGetTimeoutMs()

    /** Persisted FVF (restored on next launch via DataStore). */
    val fvfFlow: Flow<Double> = context.dataStore.data.map { it[KEY_FVF] ?: 1.0 }

    /** Persisted timeout (restored on next launch via DataStore). */
    val timeoutFlow: Flow<Int> = context.dataStore.data.map { it[KEY_TIMEOUT_MS] ?: 5000 }

    suspend fun persistFvf(fvf: Double) {
        setFvf(fvf)
        context.dataStore.edit { it[KEY_FVF] = fvf }
    }

    suspend fun persistTimeoutMs(ms: Int) {
        setTimeoutMs(ms)
        context.dataStore.edit { it[KEY_TIMEOUT_MS] = ms }
    }
}
