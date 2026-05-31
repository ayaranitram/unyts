package com.unyts.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.unyts.app.viewmodel.ConvertViewModel

@Composable
fun SettingsScreen(
    viewModel: ConvertViewModel,
    modifier: Modifier = Modifier,
) {
    val state by viewModel.uiState.collectAsState()

    // Local text state so the user can type freely before pressing Apply.
    var fvfText     by remember(state.fvf)       { mutableStateOf(state.fvf.toString()) }
    var timeoutText by remember(state.timeoutMs) { mutableStateOf(state.timeoutMs.toString()) }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("Settings", style = MaterialTheme.typography.headlineSmall)

        // ── Formation Volume Factor ───────────────────────────────────────────
        OutlinedTextField(
            value         = fvfText,
            onValueChange = { fvfText = it },
            label         = { Text("Formation Volume Factor (FVF)") },
            supportingText = { Text("Default: 1.0  — used in oil-field volume conversions") },
            modifier      = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            singleLine    = true,
        )
        Button(
            onClick  = {
                val v = fvfText.toDoubleOrNull()
                if (v != null && v > 0.0) viewModel.onUpdateFvf(v)
            },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Apply FVF") }

        HorizontalDivider()

        // ── Search timeout ────────────────────────────────────────────────────
        OutlinedTextField(
            value         = timeoutText,
            onValueChange = { timeoutText = it },
            label         = { Text("Search timeout (ms)") },
            supportingText = { Text("Default: 5000  — increase for deep multi-hop conversions") },
            modifier      = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            singleLine    = true,
        )
        Button(
            onClick  = {
                val ms = timeoutText.toIntOrNull()
                if (ms != null && ms > 0) viewModel.onUpdateTimeoutMs(ms)
            },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Apply Timeout") }

        HorizontalDivider()

        // ── Info ──────────────────────────────────────────────────────────────
        Text(
            text  = "Engine: unyts ${state.allUnits.size} units loaded",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(
            text  = "Version: ${viewModel.service.version}",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
