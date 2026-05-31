import SwiftUI

/// Root tab bar.  Tabs: Convert | History | Settings.
struct ContentView: View {

    var body: some View {
        TabView {
            ConvertView()
                .tabItem {
                    Label("Convert", systemImage: "arrow.left.arrow.right")
                }
            HistoryView()
                .tabItem {
                    Label("History", systemImage: "clock")
                }
            SettingsView()
                .tabItem {
                    Label("Settings", systemImage: "gearshape")
                }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
