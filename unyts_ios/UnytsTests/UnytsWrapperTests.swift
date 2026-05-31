import XCTest
@testable import unyts_ios   // ← replace with your actual module name if different

/**
 * Unit tests for the Objective-C++ bridge and Swift service layer.
 *
 * These are XCTest *unit* tests (UnytsTests target, not UnytsUITests).
 * They link against libunyts.a so no device / simulator is needed —
 * they run on the macOS host via the test host.
 *
 * To add this target in Xcode:
 *   File ▸ New ▸ Target ▸ Unit Testing Bundle
 *   Product Name: UnytsTests
 *   Link against: libunyts.a (add under Build Phases ▸ Link Binary With Libraries)
 *   Set the Bridging Header in Build Settings to the same
 *   unyts_ios-Bridging-Header.h used by the app target.
 */
final class UnytsWrapperTests: XCTestCase {

    var wrapper: UnytsWrapper!

    override func setUp() {
        super.setUp()
        wrapper = UnytsWrapper()
    }

    override func tearDown() {
        wrapper = nil
        super.tearDown()
    }

    // ── Basic conversion ──────────────────────────────────────────────────────

    func testMetresToFeet() throws {
        var result = 0.0
        let ok = wrapper.convertValue(1.0, fromUnit: "m", toUnit: "ft",
                                      outValue: &result, error: nil)
        XCTAssertTrue(ok)
        XCTAssertEqual(result, 3.28084, accuracy: 1e-4)
    }

    func testKilogramsToLbs() throws {
        var result = 0.0
        let ok = wrapper.convertValue(1.0, fromUnit: "kg", toUnit: "lb",
                                      outValue: &result, error: nil)
        XCTAssertTrue(ok)
        XCTAssertEqual(result, 2.20462, accuracy: 1e-4)
    }

    func testInchesToCentimetres() throws {
        var result = 0.0
        let ok = wrapper.convertValue(1.0, fromUnit: "in", toUnit: "cm",
                                      outValue: &result, error: nil)
        XCTAssertTrue(ok)
        XCTAssertEqual(result, 2.54, accuracy: 1e-6)
    }

    func testPsiToBar() throws {
        var result = 0.0
        let ok = wrapper.convertValue(1.0, fromUnit: "psi", toUnit: "bar",
                                      outValue: &result, error: nil)
        XCTAssertTrue(ok)
        XCTAssertGreaterThan(result, 0)
    }

    // ── Failure path ──────────────────────────────────────────────────────────

    func testUnknownUnitReturnsError() {
        var result = 0.0
        var error: NSError?
        let ok = wrapper.convertValue(1.0, fromUnit: "zonk", toUnit: "blarg",
                                      outValue: &result, error: &error)
        XCTAssertFalse(ok)
        XCTAssertNotNil(error)
        XCTAssertEqual(error?.domain, "com.unyts")
    }

    func testIncompatibleUnitsReturnsError() {
        var result = 0.0
        var error: NSError?
        let ok = wrapper.convertValue(1.0, fromUnit: "kg", toUnit: "m",
                                      outValue: &result, error: &error)
        XCTAssertFalse(ok)
        XCTAssertNotNil(error)
    }

    // ── Convertible check ─────────────────────────────────────────────────────

    func testConvertibleMtoFt() {
        XCTAssertTrue(wrapper.isConvertibleFrom("m", to: "ft"))
    }

    func testNotConvertibleKgToM() {
        XCTAssertFalse(wrapper.isConvertibleFrom("kg", to: "m"))
    }

    // ── Unit list ─────────────────────────────────────────────────────────────

    func testAllUnitsIsNonEmpty() {
        let units = wrapper.allUnits()
        XCTAssertGreaterThan(units.count, 100)
    }

    func testAllUnitsIsSorted() {
        let units = wrapper.allUnits() as! [String]
        let sorted = units.sorted { $0.localizedCaseInsensitiveCompare($1) == .orderedAscending }
        XCTAssertEqual(units, sorted, "allUnits() should return a sorted array")
    }

    func testAllUnitsContainsMetres() {
        let units = wrapper.allUnits() as! [String]
        XCTAssertTrue(units.contains("m"), "Expected 'm' in allUnits()")
    }

    // ── isKnownUnit ───────────────────────────────────────────────────────────

    func testKnownUnitM() {
        XCTAssertTrue(wrapper.isKnownUnit("m"))
    }

    func testUnknownUnitReturnsNo() {
        XCTAssertFalse(wrapper.isKnownUnit("zorkblaster"))
    }

    // ── FVF roundtrip ─────────────────────────────────────────────────────────

    func testFvfRoundtrip() {
        let original = wrapper.fvf
        wrapper.fvf = 1.3
        XCTAssertEqual(wrapper.fvf, 1.3, accuracy: 1e-9)
        wrapper.fvf = original
    }

    // ── Timeout roundtrip ─────────────────────────────────────────────────────

    func testTimeoutRoundtrip() {
        let original = wrapper.timeoutMs
        wrapper.timeoutMs = 3000
        XCTAssertEqual(wrapper.timeoutMs, 3000)
        wrapper.timeoutMs = original
    }

    // ── Version ───────────────────────────────────────────────────────────────

    func testVersionIsNonEmpty() {
        XCTAssertFalse(wrapper.version.isEmpty)
    }
}

// ── UnytsService Swift tests ──────────────────────────────────────────────────

@MainActor
final class UnytsServiceTests: XCTestCase {

    var service: UnytsService!

    override func setUp() async throws {
        service = UnytsService()
    }

    func testConvertSuccess() {
        let result = service.convert(value: 1.0, from: "m", to: "ft")
        switch result {
        case .success(let v): XCTAssertEqual(v, 3.28084, accuracy: 1e-4)
        case .failure(let e): XCTFail("Expected success, got \(e)")
        }
    }

    func testConvertFailure() {
        let result = service.convert(value: 1.0, from: "kg", to: "m")
        if case .success = result { XCTFail("Expected failure") }
    }

    func testAllUnitsLazy() {
        let units = service.allUnits
        XCTAssertGreaterThan(units.count, 100)
        // Second access returns the same cached array
        XCTAssertEqual(units.count, service.allUnits.count)
    }
}
