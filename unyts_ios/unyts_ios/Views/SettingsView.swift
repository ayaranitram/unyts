import SwiftUI

struct SettingsView: View {

    @EnvironmentObject var appState: AppState

    // Local edit state so the user can type freely before tapping Apply.
    @State private var fvfText:     String = ""
    @State private var timeoutText: String = ""

    var body: some View {
        NavigationStack {
            Form {
                // ── Formation Volume Factor ───────────────────────────────────
                Section {
                    TextField("FVF", text: $fvfText)
                        .keyboardType(.decimalPad)
                    Button("Apply FVF") {
                        if let v = Double(fvfText), v > 0 { appState.fvf = v }
                    }
                } header: {
                    Text("Formation Volume Factor (FVF)")
                } footer: {
                    Text("Default: 1.0  — used in oil-field volume conversions")
                }

                // ── Timeout ───────────────────────────────────────────────────
                Section {
                    TextField("ms", text: $timeoutText)
                        .keyboardType(.numberPad)
                    Button("Apply Timeout") {
                        if let ms = Int(timeoutText), ms > 0 { appState.timeoutMs = ms }
                    }
                } header: {
                    Text("Search Timeout (ms)")
                } footer: {
                    Text("Default: 5000  — increase for deep multi-hop conversions")
                }

                // ── Info ──────────────────────────────────────────────────────
                Section("Engine") {
                    LabeledContent("Version", value: appState.service.version)
                    LabeledContent("Units loaded", value: "\(appState.service.allUnits.count)")
                }
            }
            .navigationTitle("Settings")
            .onAppear {
                fvfText     = String(appState.fvf)
                timeoutText = String(appState.timeoutMs)
            }
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(AppState())
}
