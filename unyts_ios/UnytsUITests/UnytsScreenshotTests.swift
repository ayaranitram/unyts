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

        let value = app.textFields["Value"]
        if value.waitForExistence(timeout: 10) {
            value.tap()
            value.typeText("100")
            let done = app.buttons["Done"].firstMatch
            if done.waitForExistence(timeout: 3) { done.tap() }
            app.buttons["Convert"].firstMatch.tap()
        }
        snap("02-convert-result")

        app.tabBars.buttons["History"].tap()
        snap("03-history")

        app.tabBars.buttons["Settings"].tap()
        snap("04-settings")
    }
}
