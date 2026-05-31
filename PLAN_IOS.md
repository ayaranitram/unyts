# Plan: iPhone (iOS) Application

> **Prerequisite**: The shared C++ core engine described in [PLAN_CPP_WINDOWS.md](PLAN_CPP_WINDOWS.md) must be completed (at minimum through Phase 4 — C API surface) before this plan begins.  The iOS app reuses that engine with zero modifications.
>
> **Status**: The C++ core (Phases 0–6 of the Windows plan) is **fully complete** as of 2026-05-31.  The iOS app can now begin.

---

## Progress Log

| Phase | Status | Date | Notes |
|-------|--------|------|-------|
| 0 — Prerequisites | ✅ Done | 2026-05-31 | `CMakeLists.txt` for device + simulator + XCFramework build; `.gitignore`; project directory layout |
| 1 — Bridge Layer | ✅ Done | 2026-05-31 | `UnytsWrapper.h/.mm` (full Obj-C++ impl); `UnytsService.swift`; bridging header; `AppState` with FVF + timeout + history |
| 2 — Core UI | ✅ Done | 2026-05-31 | `ConvertView` (GroupBox layout, swap button), `UnitTextField` (filtered autocomplete dropdown), `HistoryView`, `ContentView` tab bar |
| 3 — Settings + Extras | ✅ Done | 2026-05-31 | `SettingsView` (FVF, timeout, version info); `@AppStorage` persistence; history with swipe-to-delete + clear |
| 4 — Polish + Device Testing | ⬜ Not started | — | Real iPhone/iPad, VoiceOver, Privacy Manifest, app icon |
| 5 — App Store Submission | ⬜ Not started | — | TestFlight → App Store Connect review |

---

## 1. Overview

Build a native iPhone/iPad application for unyts that exposes the same unit-conversion functionality as the Python GUI, using **Swift + SwiftUI** for the UI and the **shared C++ core library** for the conversion engine.

The C++ library compiles to a static archive (`libunyts.a`) for each iOS architecture (arm64 for devices, x86_64/arm64 for Simulator).  An Objective-C++ bridge layer exposes the library to Swift via a clean Swift-friendly API.

### Goals
- iPhone and iPad support (universal app)
- Offline — no network required; all unit data embedded in the binary
- App Store distribution
- Shared conversion engine with the Windows and Android apps (no logic duplication)

---

## 2. Architecture

```
┌───────────────────────────────────────────────────────┐
│                  SwiftUI App Layer                    │
│   ContentView, ConvertView, SettingsView, etc.        │
│                   (Swift, .swift files)               │
└─────────────────────┬─────────────────────────────────┘
                      │ calls Swift class
┌─────────────────────▼─────────────────────────────────┐
│              Swift/Obj-C++ Bridge                     │
│   UnytsService.swift  ←→  UnytsWrapper.h/.mm          │
│   (Swift class wraps Objective-C++ class)             │
└─────────────────────┬─────────────────────────────────┘
                      │ calls C API  (unyts_capi.h)
┌─────────────────────▼─────────────────────────────────┐
│            C++ Core Library (libunyts.a)              │
│  (compiled for arm64 / arm64-simulator / x86_64-sim)  │
│      same source as Windows core — zero changes       │
└───────────────────────────────────────────────────────┘
```

### Why Objective-C++ bridge?
Swift cannot directly call C++ code.  The standard pattern is:
1. Write an Objective-C++ class (`.mm` file) that includes `unyts_capi.h` and wraps it in an `@interface`
2. Expose the Objective-C++ class through a bridging header so Swift sees it
3. Optionally add a thin Swift `struct`/`class` façade for a more idiomatic Swift API

---

## 3. Technology Stack

| Component | Choice | Rationale |
|---|---|---|
| UI framework | SwiftUI | Apple's modern declarative UI; excellent on iOS 16+ |
| Language (UI) | Swift 5.9+ | Apple's primary language; interops with Obj-C++ |
| Bridge language | Objective-C++ (.mm) | Only way to call C++ from Swift without the C shim |
| C++ core | Shared `libunyts.a` from [PLAN_CPP_WINDOWS.md] | No logic duplication |
| Build system (core) | CMake + iOS toolchain | `cmake -DCMAKE_SYSTEM_NAME=iOS` |
| Build system (app) | Xcode project | Standard Apple toolchain |
| Distribution | App Store via Xcode / Transporter | Standard Apple process |
| Min iOS version | iOS 16.0 | Covers ~95% of active iPhones; enables full SwiftUI feature set |

---

## 4. Project Structure

```
unyts_ios/                        ← Xcode project root
├── unyts_ios.xcodeproj/
├── unyts_ios/
│   ├── App/
│   │   ├── unyts_iosApp.swift     ← @main entry point
│   │   └── AppState.swift         ← ObservableObject for global state
│   ├── Views/
│   │   ├── ContentView.swift      ← root tab / navigation view
│   │   ├── ConvertView.swift      ← main conversion screen
│   │   ├── HistoryView.swift      ← optional: recent conversions
│   │   └── SettingsView.swift     ← FVF, algorithm, timeout
│   ├── Models/
│   │   └── ConversionModel.swift  ← data model for a conversion
│   ├── Services/
│   │   └── UnytsService.swift     ← Swift façade over the bridge
│   ├── Bridge/
│   │   ├── unyts_ios-Bridging-Header.h  ← imports UnytsWrapper.h
│   │   ├── UnytsWrapper.h         ← Objective-C++ interface declaration
│   │   └── UnytsWrapper.mm        ← Objective-C++ implementation
│   └── Resources/
│       ├── Assets.xcassets/
│       └── unyts_icon.png
├── libunyts/                      ← prebuilt or CMake-built C++ core
│   ├── include/unyts/unyts_capi.h
│   └── lib/
│       ├── libunyts.a             ← arm64 (device)
│       └── libunyts_sim.a         ← arm64 + x86_64 (Simulator xcframework)
└── CMakeLists.txt                 ← optional: CMake builds libunyts.a for iOS
```

---

## 5. Building the C++ Core for iOS

The CMake iOS toolchain (`cmake/Toolchain-iOS.cmake`) already set up in the Windows plan is used here:

```bash
# Device build (arm64)
cmake -S core/ -B build_ios_device \
  -DCMAKE_SYSTEM_NAME=iOS \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=16.0 \
  -DCMAKE_BUILD_TYPE=Release

cmake --build build_ios_device

# Simulator build (arm64 + x86_64 fat library)
cmake -S core/ -B build_ios_sim \
  -DCMAKE_SYSTEM_NAME=iOS \
  -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" \
  -DCMAKE_OSX_SYSROOT=iphonesimulator \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=16.0

cmake --build build_ios_sim

# Package as XCFramework (Xcode can consume either target)
xcodebuild -create-xcframework \
  -library build_ios_device/libunyts.a \
  -library build_ios_sim/libunyts.a \
  -output libunyts/UnytsCore.xcframework
```

This XCFramework is dragged into the Xcode project once.  No Xcode/CMake coupling after that.

---

## 6. Objective-C++ Bridge

```objc
// UnytsWrapper.h
#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface UnytsWrapper : NSObject

- (instancetype)init;

- (BOOL)convertValue:(double)value
            fromUnit:(NSString*)fromUnit
              toUnit:(NSString*)toUnit
         resultValue:(double*)resultValue
          pathString:(NSString* _Nullable *)pathString
               error:(NSError* _Nullable *)error;

- (BOOL)isConvertibleFrom:(NSString*)fromUnit
                       to:(NSString*)toUnit;

- (NSArray<NSString*>*)allUnits;

- (void)setFVF:(double)fvf;
- (double)getFVF;

@end

NS_ASSUME_NONNULL_END
```

```objc
// UnytsWrapper.mm
#import "UnytsWrapper.h"
#include "unyts_capi.h"

@implementation UnytsWrapper {
    UnytsContext* _ctx;
}

- (instancetype)init {
    self = [super init];
    if (self) { _ctx = unyts_create(); }
    return self;
}

- (void)dealloc { unyts_destroy(_ctx); }

- (BOOL)convertValue:(double)value
            fromUnit:(NSString*)fromUnit
              toUnit:(NSString*)toUnit
         resultValue:(double*)resultValue
          pathString:(NSString* _Nullable *)pathString
               error:(NSError* _Nullable *)error {
    char path[512] = {};
    double out = 0.0;
    int rc = unyts_convert(_ctx, value,
                           fromUnit.UTF8String, toUnit.UTF8String,
                           &out, path, sizeof(path));
    if (rc == 0) {
        *resultValue = out;
        if (pathString) *pathString = @(path);
        return YES;
    }
    // rc != 0 → fill NSError and return NO
    return NO;
}
// ...
@end
```

---

## 7. Swift Service Layer

```swift
// UnytsService.swift
import Foundation

@MainActor
final class UnytsService: ObservableObject {
    private let wrapper = UnytsWrapper()

    @Published var allUnits: [String] = []

    init() {
        allUnits = (wrapper.allUnits() as? [String]) ?? []
    }

    func convert(value: Double, from: String, to: String)
        -> Result<(Double, String), Error>
    {
        var result = 0.0
        var path: NSString?
        var error: NSError?
        let ok = wrapper.convertValue(value, fromUnit: from, toUnit: to,
                                      resultValue: &result,
                                      pathString: &path, error: &error)
        if ok {
            return .success((result, path as String? ?? ""))
        } else {
            return .failure(error ?? NSError(domain: "unyts", code: -1))
        }
    }

    func isConvertible(from: String, to: String) -> Bool {
        wrapper.isConvertibleFrom(from, to: to)
    }

    func setFVF(_ fvf: Double) { wrapper.setFVF(fvf) }
    func getFVF() -> Double { wrapper.getFVF() }
}
```

---

## 8. SwiftUI Main Screen

The conversion screen mirrors the Python `UnytsApp` GUI:

```swift
// ConvertView.swift (simplified)
struct ConvertView: View {
    @EnvironmentObject var service: UnytsService
    @State private var fromUnit = ""
    @State private var fromValue = ""
    @State private var toUnit = ""
    @State private var toValue = ""
    @State private var pathString = ""
    @State private var errorMessage = ""

    var body: some View {
        Form {
            Section("From") {
                UnitTextField(label: "Unit", text: $fromUnit,
                              suggestions: service.allUnits)
                TextField("Value", text: $fromValue)
                    .keyboardType(.decimalPad)
            }
            Section("To") {
                UnitTextField(label: "Unit", text: $toUnit,
                              suggestions: service.allUnits)
                TextField("Result", text: $toValue)
                    .disabled(true)
            }
            Button("Convert") { performConversion() }
            if !pathString.isEmpty {
                Text(pathString).font(.caption).foregroundColor(.secondary)
            }
            if !errorMessage.isEmpty {
                Text(errorMessage).foregroundColor(.red)
            }
        }
        .navigationTitle("Unyts")
    }

    private func performConversion() {
        guard let v = Double(fromValue) else { errorMessage = "Invalid number"; return }
        switch service.convert(value: v, from: fromUnit, to: toUnit) {
        case .success(let (result, path)):
            toValue = String(result)
            pathString = path
            errorMessage = ""
        case .failure(let err):
            toValue = ""
            errorMessage = err.localizedDescription
        }
    }
}
```

Additional screens:
- `SettingsView` — FVF input, algorithm picker (BFS/DFS/hybrid), timeout slider
- `HistoryView` — optional list of recent conversions (stored in `UserDefaults` or `SwiftData`)
- **Autocomplete**: a custom `UnitTextField` view backed by `service.allUnits` filtered by prefix as the user types

---

## 9. Phased Delivery Plan

### Phase 0 — Prerequisites (parallel with C++ core Phase 1–3)
- Set up macOS development machine with Xcode 15+, Apple Developer account
- Verify CMake iOS toolchain compiles the C++ core for arm64
- Create empty Xcode project and confirm XCFramework integration

### Phase 1 — Bridge Layer (1–2 weeks)
- Implement `UnytsWrapper.h/.mm` (all methods)
- Write Swift `UnytsService`
- Write unit tests in Swift calling `UnytsService.convert()` with known values
- **Milestone**: Swift test calls `convert(1, "meter", "foot")` and gets `3.28084`

### Phase 2 — Core UI (2–3 weeks)
- Build `ConvertView` with from/to unit fields, value fields, convert button
- Implement `UnitTextField` with autocomplete search over `allUnits`
- Handle keyboard dismissal, input validation, error display
- iPhone layout + iPad adaptive layout
- **Milestone**: basic conversion works end-to-end on iPhone Simulator

### Phase 3 — Settings + Extras (1–2 weeks)
- `SettingsView`: FVF, algorithm, timeout, print-path toggle
- Persist settings in `UserDefaults`
- Optional `HistoryView` (last 20 conversions)
- Dark mode / Dynamic Type support (SwiftUI handles most automatically)
- **Milestone**: settings survive app restart; FVF-dependent conversions work

### Phase 4 — Polish + Device Testing (1–2 weeks)
- Test on real iPhone and iPad hardware (multiple screen sizes)
- Accessibility audit (VoiceOver labels on all interactive elements)
- App icon (1024×1024 + all required sizes via `Assets.xcassets`)
- Launch screen / splash
- Privacy manifest (required by Apple since iOS 17 SDK)

### Phase 5 — App Store Submission (1 week)
- Configure `Info.plist` (bundle ID, version, usage descriptions)
- TestFlight beta distribution for testing
- App Store Connect: screenshots (6.7", 5.5"), description, keywords
- Submit for review (~1–3 days Apple review time)

---

## 10. Effort Estimate

| Phase | Duration |
|---|---|
| 0 — Prerequisites | 3–5 days |
| 1 — Bridge layer | 1–2 weeks |
| 2 — Core UI | 2–3 weeks |
| 3 — Settings + extras | 1–2 weeks |
| 4 — Polish + device testing | 1–2 weeks |
| 5 — App Store submission | 1 week |
| **Total (after C++ core done)** | **~2–2.5 months** |

> **Dependency**: The C++ core (Phases 1–4 of [PLAN_CPP_WINDOWS.md]) must be complete before Phase 1 of this plan can begin.  Total calendar time from scratch: ~6.5–8.5 months for a single developer doing both Windows and iOS sequentially.  Parallel teams reduce this significantly.

---

## 11. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Apple Developer Program required ($99/year) | Certain | Low (known cost) | Register early; free distribution to physical devices during development |
| App Store review rejection (guidelines compliance) | Medium | Medium | Review Human Interface Guidelines; unyts is a utility app with no unusual APIs |
| C++ static init order issues when built as XCFramework | Medium | Medium | Replace any static globals with lazy-init singletons; test on device early |
| SwiftUI autocomplete list performance with thousands of unit names | Low | Low | Use `LazyVStack` + debounced filtering; prefix trie if needed |
| Xcode version pinning — XCFramework compatibility | Low | Low | Document minimum Xcode version (15.x); test on CI with Xcode matrix |
| Privacy Manifest requirements (Apple added 2024) | Medium | Medium | Review required reason APIs; unyts uses no network / location / health APIs, so manifest should be minimal |

---

## 12. Prerequisites / Tools Required

| Tool | Notes |
|---|---|
| macOS 14+ (Sonoma) | Required to run Xcode 15+ |
| Xcode 15+ | Apple's IDE; mandatory for iOS builds |
| Apple Developer account | $99/year for App Store distribution; free for simulator |
| CMake 3.21+ | To cross-compile C++ core for iOS |
| C++ core built (XCFramework) | From [PLAN_CPP_WINDOWS.md] Phase 0–4 |

---

## 13. Code Shared with Android

The entire `core/` C++ library and the `unyts_capi.h` interface are identical to the Android build.  **Only the bridge layer and the UI differ.**  See [PLAN_ANDROID.md](PLAN_ANDROID.md) for details on the Android side.

Shared percentage estimate:
- C++ core engine: **100% shared** between Windows, iOS, Android
- C API (`unyts_capi.h`): **100% shared**
- Bridge + UI: **0% shared** (Obj-C++/SwiftUI vs JNI/Kotlin — different languages, different UI toolkits)
