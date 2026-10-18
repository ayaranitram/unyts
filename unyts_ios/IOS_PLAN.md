# unyts iOS — findings and way forward

Status: written on Windows, **nothing here has been built or run yet**. The first
job on macOS is to validate the steps below and fix whatever breaks.

## What already exists

- `cpp/` — C++17 engine (`src/`, `include/unyts/`), C API (`capi/unyts_capi.cpp`,
  `include/unyts/unyts_capi.h`), Python bindings, Windows GUI, tests.
- `unyts_ios/` — SwiftUI app sources, ObjC++ bridge (`Bridge/UnytsWrapper.mm`),
  `CMakeLists.txt`, `build.sh`, XCTest file, privacy manifest. See `README.md`.
- `unyts_android/` — sibling JNI app using the same C API.

Architecture: SwiftUI → `AppState` → `UnytsService` → `UnytsWrapper` (ObjC++) →
`libunyts.a` (C++).

## Findings from static review

1. **Missing toolchain file.** `build.sh` expects `unyts_ios/cmake/ios.toolchain.cmake`;
   the `cmake/` folder does not exist. Fetch it from
   https://github.com/leetal/ios-cmake (README step) or switch to native CMake
   iOS support (`-DCMAKE_SYSTEM_NAME=iOS`, as in the comments of `CMakeLists.txt`).
2. **Simulator slice is arm64 only.** `build.sh` builds `SIMULATORARM64` and only
   lipo-merges an x86_64 build if `build/simulator_x86/...` exists, but nothing
   creates it. Fine on Apple Silicon Macs; Intel Macs need a second build with
   `-DPLATFORM=SIMULATOR64`.
3. **Output paths assume the Xcode generator** (`Release-iphoneos/`,
   `Release-iphonesimulator/`). Matches `-G Xcode`; verify after the first build.
4. **Two build recipes disagree** (comment block in `CMakeLists.txt` vs `build.sh`,
   different XCFramework names/paths: `UnytsCore.xcframework` vs
   `build/unyts.xcframework`). Pick one (suggest `build.sh`) and delete the other.
5. **No embedded-data problem.** The C++ source does not read unit/data files at
   runtime (only an optional graph cache via `default_cache_path()` which uses
   `std::filesystem::temp_directory_path()`; on iOS this resolves to the app's
   `tmp` directory, which can be purged — acceptable for a cache). Consider
   pointing it at Caches via the wrapper if startup time matters.
6. **No `.xcodeproj`.** Must be created manually (README) — error-prone. Option:
   add an `xcodegen` `project.yml` so the project is reproducible from git.
7. **`-Wall -Wextra` on iOS Clang** may surface warnings not seen with MSVC/GCC;
   not expected to be fatal.
8. Deployment target is iOS 16 (needed by `ContentUnavailableView` in
   `HistoryView`; note that view is actually iOS 17+ — verify and either raise the
   target to 17 or replace it with a custom empty-state view).

## Plan (macOS)

1. `brew install cmake` (optionally `xcodegen`); install Xcode 15+.
2. Add the toolchain: clone ios-cmake into `unyts_ios/cmake/`.
3. `cd unyts_ios && ./build.sh` → `build/unyts.xcframework`. Fix path/arch issues.
4. Sanity-test the C++ core on the Mac first: configure `cpp/` with plain CMake and
   run `cpp/tests/test_core.cpp`.
5. Create the Xcode project per `README.md` (or add xcodegen spec), link the
   XCFramework (Do Not Embed), set the bridging header, add the privacy manifest.
6. Build for simulator; run `UnytsTests` (⌘U). Fix `UnytsWrapper.mm` / Swift
   compile errors (likely first failures: header search paths, `.mm` not in
   target, `ContentUnavailableView` availability).
7. Manual UI pass: conversion, autocomplete, history persistence, settings.
8. Polish for release: app icon (reuse `unyts_icon_web.png`), launch screen,
   bundle ID/team signing, privacy policy URL, screenshots.
9. TestFlight upload (Apple Developer Program required), then App Store review.
10. Optional: GitHub Actions `macos-14` workflow running steps 3–6 to keep it green.

## Open questions

- App name/bundle ID (`com.unyts.app` is a placeholder).
- iOS minimum version (16 vs 17, see finding 8).
- Free vs paid; any analytics (affects `PrivacyInfo.xcprivacy`).
