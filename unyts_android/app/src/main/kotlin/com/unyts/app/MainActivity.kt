package com.unyts.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.SwapHoriz
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.unyts.app.ui.ConvertScreen
import com.unyts.app.ui.SettingsScreen
import com.unyts.app.ui.theme.UnytsTheme
import com.unyts.app.viewmodel.ConvertViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            UnytsTheme {
                UnytsApp()
            }
        }
    }
}

@Composable
fun UnytsApp(viewModel: ConvertViewModel = viewModel()) {
    var selectedTab by remember { mutableIntStateOf(0) }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick  = { selectedTab = 0 },
                    icon     = { Icon(Icons.Default.SwapHoriz, contentDescription = "Convert") },
                    label    = { Text("Convert") },
                )
                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick  = { selectedTab = 1 },
                    icon     = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                    label    = { Text("Settings") },
                )
            }
        }
    ) { innerPadding ->
        when (selectedTab) {
            0 -> ConvertScreen(viewModel, Modifier.padding(innerPadding))
            1 -> SettingsScreen(viewModel, Modifier.padding(innerPadding))
        }
    }
}
