# unyts — iOS App

SwiftUI unit-conversion app powered by the same C++ engine as the desktop version.

---

## Project layout

```
unyts_ios/
├── CMakeLists.txt                  # Builds libunyts.a (device + simulator)
├── build.sh                        # One-shot macOS build helper
├── UnytsTests/
│   └── UnytsWrapperTests.swift     # XCTest unit + service tests
└── unyts_ios/
    ├── App/
    │   ├── AppState.swift          # @EnvironmentObject — all shared state
    │   ├── Info.plist
    │   └── unyts_iosApp.swift      # @main entry point
    ├── Assets.xcassets/
    ├── Bridge/
    │   ├── UnytsWrapper.h          # ObjC header exposed to Swift
    │   ├── UnytsWrapper.mm         # ObjC++ implementation (includes C++ headers)
    │   └── unyts_ios-Bridging-Header.h
    ├── Models/
    │   └── ConversionModel.swift   # ConversionRecord (Identifiable, Codable)
    ├── PrivacyInfo.xcprivacy
    ├── Services/
    │   └── UnytsService.swift      # @MainActor Swift facade over UnytsWrapper
    └── Views/
        ├── ContentView.swift       # TabView root
        ├── ConvertView.swift
        ├── HistoryView.swift
        ├── SettingsView.swift
        └── UnitTextField.swift     # Autocomplete text field
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Xcode | 15+ |
| iOS Deployment Target | 16.0 |
| CMake | 3.21+ (`brew install cmake`) |
| ios-cmake toolchain | See below |

Install the [ios-cmake](https://github.com/leetal/ios-cmake) toolchain (one option):

```bash
git clone https://github.com/leetal/ios-cmake.git
cp ios-cmake/ios.toolchain.cmake unyts_ios/cmake/ios.toolchain.cmake
```

---

## Build libunyts.a and package as XCFramework

```bash
cd unyts_ios
chmod +x build.sh
./build.sh
```

Output: `build/unyts.xcframework`

---

## Create the Xcode project

Xcode projects (`.xcodeproj`) are not stored in git because they embed
absolute paths and developer team IDs.  Create one from scratch:

1. **Xcode ▸ New ▸ Project ▸ iOS ▸ App**
   - Product Name: `unyts_ios`
   - Bundle ID: `com.unyts.app`
   - Interface: SwiftUI
   - Language: Swift

2. **Delete** the generated `ContentView.swift` and `<AppName>App.swift`.

3. **Add existing files** — drag the entire `unyts_ios/unyts_ios/` folder into
   the Xcode project navigator (check *Copy items if needed* = **off**).

4. **Add the XCFramework** — drag `build/unyts.xcframework` into
   *Frameworks, Libraries, and Embedded Content*; set to **Do Not Embed**
   (static library).

5. **Set the bridging header** in Build Settings ▸ Swift Compiler – General:
   ```
   Objective-C Bridging Header = unyts_ios/Bridge/unyts_ios-Bridging-Header.h
   ```

6. **Add `PrivacyInfo.xcprivacy`** to the app target's *Copy Bundle Resources*
   build phase.

7. Set `MARKETING_VERSION = 1.0.0` and `CURRENT_PROJECT_VERSION = 1` in the
   project build settings.

---

## Run the tests

In Xcode:

1. **File ▸ New ▸ Target ▸ Unit Testing Bundle**
   - Product Name: `UnytsTests`
   - Host Application: `unyts_ios`

2. Delete the generated test stub; add `UnytsTests/UnytsWrapperTests.swift`
   to the new target.

3. Link `libunyts.a` (or the XCFramework) in Build Phases ▸
   Link Binary With Libraries.

4. Set the same bridging header as the app target.

5. **Product ▸ Test** (`⌘U`)

---

## Minimum deployment target

iOS 16.0 — required for `ContentUnavailableView` used in `HistoryView`.

---

## Architecture

```
SwiftUI Views
    └── @EnvironmentObject AppState
            └── UnytsService   (@MainActor, lazy allUnits)
                    └── UnytsWrapper   (ObjC++)
                            └── unyts_capi.h / libunyts.a   (C++)
```
