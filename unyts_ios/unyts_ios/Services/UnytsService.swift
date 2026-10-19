import Foundation

/**
 * Swift façade over the Objective-C++ UnytsWrapper.
 *
 * Annotated @MainActor because the underlying UnytsWrapper holds a C pointer
 * that must not be accessed concurrently.  Heavy operations (unit list loading)
 * are cheap enough on this engine that main-thread access is acceptable; call
 * convert() from a Task if needed.
 */
@MainActor
final class UnytsService: ObservableObject {

    private let wrapper = UnytsWrapper()

    // ── Unit names ────────────────────────────────────────────────────────────

    /// All known unit names, sorted, loaded once on first access.
    lazy var allUnits: [String] = wrapper.allUnits()

    var version: String { wrapper.version }

    // ── Conversion ────────────────────────────────────────────────────────────

    func convert(value: Double, from: String, to: String) -> Result<Double, Error> {
        var result = 0.0
        do {
            try wrapper.convertValue(value, fromUnit: from, toUnit: to, outValue: &result)
            return .success(result)
        } catch {
            return .failure(error)
        }
    }

    func isConvertible(from: String, to: String) -> Bool {
        wrapper.isConvertible(from: from, to: to)
    }

    func isKnownUnit(_ unit: String) -> Bool {
        wrapper.isKnownUnit(unit)
    }

    // ── Settings ──────────────────────────────────────────────────────────────

    var fvf: Double {
        get { wrapper.fvf }
        set { wrapper.fvf = newValue }
    }

    var timeoutMs: Int {
        get { wrapper.timeoutMs }
        set { wrapper.timeoutMs = newValue }
    }
}
