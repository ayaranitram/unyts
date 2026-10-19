import XCTest

/// Walks through the main screens and attaches a screenshot of each one.
/// CI exports the attachments from the .xcresult bundle (see ios.yml).
final class UnytsScreenshotTests: XCTestCase {

    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    private func snap(_ name: String) {
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }

    func testCaptureScreens() throws {
        let app = XCUIApplication()
        app.launch()

        snap("01-convert-empty")

        let fields = app.textFields
        if fields.element(boundBy: 2).waitForExistence(timeout: 10) {
            enterUnit("m", in: fields.element(boundBy: 0), app: app)
            enterUnit("ft", in: fields.element(boundBy: 2), app: app)
        }

        let value = fields.element(boundBy: 1)
        if value.waitForExistence(timeout: 10) {
            value.tap()
            value.typeText("100")
            let done = app.buttons["Done"].firstMatch
            if done.waitForExistence(timeout: 3) { done.tap() }
            app.buttons["convertButton"].tap()
        }
        sleep(1)
        snap("02-convert-result")

        app.tabBars.buttons["History"].tap()
        sleep(1)
        snap("03-history")

        app.tabBars.buttons["Settings"].tap()
        sleep(1)
        snap("04-settings")
    }

    /// Types a unit and dismisses the suggestion list by picking the exact match if shown.
    private func enterUnit(_ unit: String, in field: XCUIElement, app: XCUIApplication) {
        field.tap()
        field.typeText(unit)
        let suggestion = app.buttons[unit].firstMatch
        if suggestion.waitForExistence(timeout: 2) { suggestion.tap() }
    }
}
