package com.unyts.app.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.unyts.app.jni.UnytsService
import com.unyts.app.model.ConversionRecord
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

data class ConvertUiState(
    val fromUnit:     String  = "",
    val fromValue:    String  = "",
    val toUnit:       String  = "",
    val toValue:      String  = "",
    val errorMessage: String  = "",
    val allUnits:     List<String> = emptyList(),
    val isLoading:    Boolean = false,
    val fvf:          Double  = 1.0,
    val timeoutMs:    Int     = 5000,
    val history:      List<ConversionRecord> = emptyList(),
)

class ConvertViewModel(app: Application) : AndroidViewModel(app) {

    val service = UnytsService(app.applicationContext)

    private val _uiState = MutableStateFlow(ConvertUiState())
    val uiState: StateFlow<ConvertUiState> = _uiState.asStateFlow()

    init {
        // Load all unit names on a background thread.
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val units = withContext(Dispatchers.Default) { service.allUnits }
            _uiState.update { it.copy(allUnits = units, isLoading = false) }
        }
        // Restore persisted FVF.
        viewModelScope.launch {
            service.fvfFlow.collect { fvf ->
                service.setFvf(fvf)
                _uiState.update { it.copy(fvf = fvf) }
            }
        }
        // Restore persisted timeout.
        viewModelScope.launch {
            service.timeoutFlow.collect { ms ->
                service.setTimeoutMs(ms)
                _uiState.update { it.copy(timeoutMs = ms) }
            }
        }
    }

    // ── Input handlers ────────────────────────────────────────────────────────

    fun onFromUnitChange(v: String)  = _uiState.update { it.copy(fromUnit  = v, errorMessage = "") }
    fun onToUnitChange(v: String)    = _uiState.update { it.copy(toUnit    = v, errorMessage = "") }
    fun onFromValueChange(v: String) = _uiState.update { it.copy(fromValue = v, errorMessage = "") }

    // ── Conversion ────────────────────────────────────────────────────────────

    fun onConvert() {
        val state = _uiState.value
        val value = state.fromValue.toDoubleOrNull()
        if (value == null) {
            _uiState.update { it.copy(errorMessage = "Invalid number") }
            return
        }
        viewModelScope.launch {
            service.convert(value, state.fromUnit, state.toUnit)
                .onSuccess { result ->
                    val record = ConversionRecord(
                        fromValue = value,
                        fromUnit  = state.fromUnit,
                        toValue   = result,
                        toUnit    = state.toUnit,
                    )
                    _uiState.update {
                        val newHistory = (listOf(record) + it.history).take(50)
                        it.copy(toValue = formatResult(result), errorMessage = "", history = newHistory)
                    }
                }
                .onFailure { err ->
                    _uiState.update { it.copy(toValue = "", errorMessage = err.message ?: "Conversion failed") }
                }
        }
    }

    /** Reverse conversion: uses the current result value as the new input. */
    fun onReverseConvert() {
        val state = _uiState.value
        val value = state.toValue.toDoubleOrNull() ?: return
        viewModelScope.launch {
            service.convert(value, state.toUnit, state.fromUnit)
                .onSuccess { result ->
                    _uiState.update { it.copy(fromValue = formatResult(result), errorMessage = "") }
                }
                .onFailure { err ->
                    _uiState.update { it.copy(errorMessage = err.message ?: "Conversion failed") }
                }
        }
    }

    fun onSwapUnits() {
        _uiState.update {
            it.copy(
                fromUnit  = it.toUnit,   toUnit  = it.fromUnit,
                fromValue = it.toValue,  toValue = it.fromValue,
            )
        }
    }

    // ── Settings ──────────────────────────────────────────────────────────────

    fun onUpdateFvf(fvf: Double) {
        viewModelScope.launch { service.persistFvf(fvf) }
        _uiState.update { it.copy(fvf = fvf) }
    }

    fun onUpdateTimeoutMs(ms: Int) {
        viewModelScope.launch { service.persistTimeoutMs(ms) }
        _uiState.update { it.copy(timeoutMs = ms) }
    }

    fun onClearHistory() {
        _uiState.update { it.copy(history = emptyList()) }
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private fun formatResult(value: Double): String {
        if (value % 1.0 == 0.0 && kotlin.math.abs(value) < 1e15) return value.toLong().toString()
        return "%.8g".format(value).trimEnd('0').trimEnd('.')
    }
}
