import SwiftUI

struct HistoryView: View {

    @EnvironmentObject var appState: AppState

    var body: some View {
        NavigationStack {
            Group {
                if appState.history.isEmpty {
                    ContentUnavailableView(
                        "No history yet",
                        systemImage: "clock",
                        description: Text("Completed conversions will appear here.")
                    )
                } else {
                    List {
                        ForEach(appState.history) { record in
                            HistoryRow(record: record)
                        }
                        .onDelete { indices in
                            appState.history.remove(atOffsets: indices)
                        }
                    }
                }
            }
            .navigationTitle("History")
            .toolbar {
                if !appState.history.isEmpty {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("Clear", role: .destructive) {
                            appState.clearHistory()
                        }
                    }
                }
            }
        }
    }
}

private struct HistoryRow: View {
    let record: ConversionRecord

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("\(formatValue(record.fromValue)) \(record.fromUnit)  →  \(formatValue(record.toValue)) \(record.toUnit)")
                .font(.body)
            Text(record.date.formatted(date: .abbreviated, time: .shortened))
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 2)
    }

    private func formatValue(_ v: Double) -> String {
        if v.truncatingRemainder(dividingBy: 1) == 0, abs(v) < 1e15 { return String(Int64(v)) }
        return String(format: "%.6g", v)
    }
}

#Preview {
    HistoryView()
        .environmentObject(AppState())
}
