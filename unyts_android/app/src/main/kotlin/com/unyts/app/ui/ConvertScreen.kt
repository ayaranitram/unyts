package com.unyts.app.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.SwapVert
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.unyts.app.viewmodel.ConvertViewModel

@Composable
fun ConvertScreen(
    viewModel: ConvertViewModel,
    modifier: Modifier = Modifier,
) {
    val state       by viewModel.uiState.collectAsState()
    val focusManager = LocalFocusManager.current

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text("Unyts Converter", style = MaterialTheme.typography.headlineSmall)

        // ── From ──────────────────────────────────────────────────────────────
        UnitAutoCompleteField(
            label    = "From unit",
            value    = state.fromUnit,
            allUnits = state.allUnits,
            onChange = viewModel::onFromUnitChange,
        )
        OutlinedTextField(
            value         = state.fromValue,
            onValueChange = viewModel::onFromValueChange,
            label         = { Text("Value") },
            modifier      = Modifier.fillMaxWidth(),
            keyboardOptions = KeyboardOptions(
                keyboardType = KeyboardType.Decimal,
                imeAction    = ImeAction.Done,
            ),
            keyboardActions = KeyboardActions(onDone = {
                focusManager.clearFocus()
                viewModel.onConvert()
            }),
            singleLine = true,
        )

        // ── Swap button ───────────────────────────────────────────────────────
        Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
            IconButton(onClick = viewModel::onSwapUnits) {
                Icon(Icons.Default.SwapVert, contentDescription = "Swap units")
            }
        }

        // ── To ────────────────────────────────────────────────────────────────
        UnitAutoCompleteField(
            label    = "To unit",
            value    = state.toUnit,
            allUnits = state.allUnits,
            onChange = viewModel::onToUnitChange,
        )
        OutlinedTextField(
            value         = state.toValue,
            onValueChange = {},
            label         = { Text("Result") },
            modifier      = Modifier.fillMaxWidth(),
            readOnly      = true,
            singleLine    = true,
        )

        // ── Convert button ────────────────────────────────────────────────────
        Spacer(Modifier.height(4.dp))
        Button(
            onClick  = { focusManager.clearFocus(); viewModel.onConvert() },
            modifier = Modifier.fillMaxWidth(),
            enabled  = !state.isLoading,
        ) {
            if (state.isLoading)
                CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
            else
                Text("Convert")
        }

        // ── Error ─────────────────────────────────────────────────────────────
        if (state.errorMessage.isNotEmpty()) {
            Text(
                text  = state.errorMessage,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

/**
 * Text field with a list of up to 10 unit name suggestions filtered by the
 * current input (case-insensitive substring match). Suggestions are shown to
 * the right of the input field so they never obscure it, and focus stays on
 * the text field while typing.
 */
@Composable
fun UnitAutoCompleteField(
    label:    String,
    value:    String,
    allUnits: List<String>,
    onChange: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    var showSuggestions by remember { mutableStateOf(false) }
    val suggestions = remember(value, allUnits) {
        if (value.isBlank()) emptyList()
        else allUnits.filter { it.contains(value, ignoreCase = true) }.take(10)
    }

    Row(
        modifier          = modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top,
    ) {
        OutlinedTextField(
            value         = value,
            onValueChange = { onChange(it); showSuggestions = it.isNotBlank() },
            label         = { Text(label) },
            modifier      = Modifier.weight(1f),
            singleLine    = true,
        )
        if (showSuggestions && suggestions.isNotEmpty()) {
            Card(
                modifier  = Modifier
                    .width(180.dp)
                    .heightIn(max = 200.dp)
                    .padding(start = 4.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
            ) {
                LazyColumn {
                    items(suggestions) { unit ->
                        Text(
                            text     = unit,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { onChange(unit); showSuggestions = false }
                                .padding(horizontal = 8.dp, vertical = 6.dp),
                            style    = MaterialTheme.typography.bodyMedium,
                        )
                        HorizontalDivider()
                    }
                }
            }
        }
    }
}
