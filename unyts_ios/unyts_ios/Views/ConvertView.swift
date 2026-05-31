import SwiftUI

struct ConvertView: View {

    @EnvironmentObject var appState: AppState
    @FocusState private var focusedField: Field?

    private enum Field { case fromValue }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 16) {

                    // ── From ──────────────────────────────────────────────────
                    GroupBox("From") {
                        VStack(spacing: 8) {
                            UnitTextField(
                                label:    "Unit",
                                text:     $appState.fromUnit,
                                allUnits: appState.service.allUnits
                            )
                            TextField("Value", text: $appState.fromValue)
                                .keyboardType(.decimalPad)
                                .focused($focusedField, equals: .fromValue)
                                .padding(10)
                                .background(Color(.systemGray6))
                                .cornerRadius(8)
                        }
                    }

                    // ── Swap ──────────────────────────────────────────────────
                    Button {
                        appState.swapUnits()
                    } label: {
                        Image(systemName: "arrow.up.arrow.down.circle.fill")
                            .font(.title)
                            .foregroundStyle(.tint)
                    }
                    .buttonStyle(.plain)

                    // ── To ────────────────────────────────────────────────────
                    GroupBox("To") {
                        VStack(spacing: 8) {
                            UnitTextField(
                                label:    "Unit",
                                text:     $appState.toUnit,
                                allUnits: appState.service.allUnits
                            )
                            Text(appState.toValue.isEmpty ? "—" : appState.toValue)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(10)
                                .background(Color(.systemGray6))
                                .cornerRadius(8)
                                .foregroundStyle(appState.toValue.isEmpty ? .secondary : .primary)
                        }
                    }

                    // ── Convert button ────────────────────────────────────────
                    Button {
                        focusedField = nil
                        appState.convert()
                    } label: {
                        Label("Convert", systemImage: "equal.circle.fill")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)

                    // ── Error message ─────────────────────────────────────────
                    if !appState.errorMessage.isEmpty {
                        Label(appState.errorMessage, systemImage: "exclamationmark.triangle")
                            .foregroundStyle(.red)
                            .font(.caption)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }

                    Spacer(minLength: 40)
                }
                .padding()
            }
            .navigationTitle("Unyts")
            .toolbar {
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Done") { focusedField = nil }
                }
            }
        }
    }
}

#Preview {
    ConvertView()
        .environmentObject(AppState())
}
