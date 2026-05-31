package com.unyts.app.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.unyts.app.model.ConversionRecord
import com.unyts.app.viewmodel.ConvertViewModel

@Composable
fun HistoryScreen(
    viewModel: ConvertViewModel,
    modifier:  Modifier = Modifier,
) {
    val state by viewModel.uiState.collectAsState()

    Column(modifier = modifier.fillMaxSize()) {
        // ── Toolbar row ───────────────────────────────────────────────────────
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment    = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text("History", style = MaterialTheme.typography.headlineSmall)
            if (state.history.isNotEmpty()) {
                IconButton(onClick = viewModel::onClearHistory) {
                    Icon(
                        imageVector        = Icons.Default.Delete,
                        contentDescription = "Clear history",
                        tint               = MaterialTheme.colorScheme.error,
                    )
                }
            }
        }

        if (state.history.isEmpty()) {
            // ── Empty state ───────────────────────────────────────────────────
            Box(
                modifier        = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text  = "No history yet.\nCompleted conversions will appear here.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        } else {
            LazyColumn(
                contentPadding         = PaddingValues(horizontal = 16.dp, vertical = 4.dp),
                verticalArrangement    = Arrangement.spacedBy(8.dp),
                modifier               = Modifier.fillMaxSize(),
            ) {
                items(
                    items = state.history,
                    key   = { it.id },
                ) { record ->
                    HistoryCard(record)
                }
            }
        }
    }
}

@Composable
private fun HistoryCard(record: ConversionRecord) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text     = "${formatValue(record.fromValue)} ${record.fromUnit}",
                    style    = MaterialTheme.typography.bodyMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text     = "→  ${formatValue(record.toValue)} ${record.toUnit}",
                    style    = MaterialTheme.typography.bodyMedium,
                    color    = MaterialTheme.colorScheme.primary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
    }
}

private fun formatValue(value: Double): String {
    if (value % 1.0 == 0.0 && kotlin.math.abs(value) < 1e15) return value.toLong().toString()
    return "%.6g".format(value).trimEnd('0').trimEnd('.')
}
