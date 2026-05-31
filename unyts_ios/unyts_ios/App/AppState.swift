import SwiftUI

/**
 * Global application state shared via @EnvironmentObject.
 * Holds all user-editable fields and delegates to UnytsService for conversion.
 */
@MainActor
final class AppState: ObservableObject {

    let service = UnytsService()

    // ── Conversion fields ─────────────────────────────────────────────────────
    @Published var fromUnit:     String = ""
    @Published var fromValue:    String = ""
    @Published var toUnit:       String = ""
    @Published var toValue:      String = ""
    @Published var errorMessage: String = ""

    // ── Conversion history ────────────────────────────────────────────────────
    @Published var history: [ConversionRecord] = []

    // ── Persisted settings ────────────────────────────────────────────────────
    @AppStorage("fvf")       private var storedFvf:       Double = 1.0
    @AppStorage("timeoutMs") private var storedTimeoutMs: Int    = 5000

    var fvf: Double {
        get { storedFvf }
        set { storedFvf = newValue; service.fvf = newValue }
    }

    var timeoutMs: Int {
        get { storedTimeoutMs }
        set { storedTimeoutMs = newValue; service.timeoutMs = newValue }
    }

    init() {
        // Restore persisted settings into the native context.
        service.fvf       = storedFvf
        service.timeoutMs = storedTimeoutMs
    }

    // ── Actions ───────────────────────────────────────────────────────────────

    func convert() {
        guard let value = Double(fromValue) else {
            errorMessage = "Invalid number"
            return
        }
        switch service.convert(value: value, from: fromUnit, to: toUnit) {
        case .success(let result):
            toValue      = formatResult(result)
            errorMessage = ""
            history.insert(
                ConversionRecord(id: UUID(), fromValue: value, fromUnit: fromUnit,
                                 toValue: result, toUnit: toUnit, date: Date()),
                at: 0
            )
            if history.count > 50 { history = Array(history.prefix(50)) }
        case .failure(let error):
            toValue      = ""
            errorMessage = error.localizedDescription
        }
    }

    func swapUnits() {
        swap(&fromUnit,  &toUnit)
        swap(&fromValue, &toValue)
    }

    func clearHistory() { history.removeAll() }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private func formatResult(_ value: Double) -> String {
        if value.truncatingRemainder(dividingBy: 1) == 0, abs(value) < 1e15 {
            return String(Int64(value))
        }
        return String(format: "%.8g", value)
    }
}
