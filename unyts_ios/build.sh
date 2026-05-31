#!/usr/bin/env bash
# build.sh — macOS build helper for unyts_ios
# ─────────────────────────────────────────────────────────────────────────────
# Builds libunyts.a for both device (arm64) and simulator (arm64+x86_64),
# then packages them into an XCFramework.
#
# Prerequisites:
#   • Xcode 15+ and Command Line Tools installed
#   • CMake 3.21+ on PATH  (brew install cmake)
#
# Usage:
#   chmod +x build.sh
#   ./build.sh
#
# Output:
#   build/unyts.xcframework/   ← add this to your Xcode project
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"

IOS_TOOLCHAIN="${SCRIPT_DIR}/cmake/ios.toolchain.cmake"

# ── 1. Build for iOS device (arm64) ──────────────────────────────────────────
echo "==> Building for iOS device (arm64)..."
cmake -S "${SCRIPT_DIR}" \
      -B "${BUILD_DIR}/device" \
      -G Xcode \
      -DCMAKE_TOOLCHAIN_FILE="${IOS_TOOLCHAIN}" \
      -DPLATFORM=OS64 \
      -DCMAKE_BUILD_TYPE=Release

cmake --build "${BUILD_DIR}/device" \
      --config Release \
      --target unyts

# ── 2. Build for iOS Simulator (arm64 + x86_64) ───────────────────────────────
echo "==> Building for iOS Simulator..."
cmake -S "${SCRIPT_DIR}" \
      -B "${BUILD_DIR}/simulator" \
      -G Xcode \
      -DCMAKE_TOOLCHAIN_FILE="${IOS_TOOLCHAIN}" \
      -DPLATFORM=SIMULATORARM64 \
      -DCMAKE_BUILD_TYPE=Release

cmake --build "${BUILD_DIR}/simulator" \
      --config Release \
      --target unyts

# ── 3. Lipo-merge simulator slices if needed ─────────────────────────────────
SIM_LIB_ARM64="${BUILD_DIR}/simulator/Release-iphonesimulator/libunyts.a"
SIM_LIB_X86="${BUILD_DIR}/simulator_x86/Release-iphonesimulator/libunyts.a"

if [[ -f "${SIM_LIB_X86}" ]]; then
    echo "==> Creating fat simulator library..."
    lipo -create "${SIM_LIB_ARM64}" "${SIM_LIB_X86}" \
         -output "${BUILD_DIR}/libunyts-simulator-fat.a"
    SIM_LIB_FINAL="${BUILD_DIR}/libunyts-simulator-fat.a"
else
    SIM_LIB_FINAL="${SIM_LIB_ARM64}"
fi

# ── 4. Package into XCFramework ───────────────────────────────────────────────
echo "==> Packaging XCFramework..."
XCFW="${BUILD_DIR}/unyts.xcframework"
rm -rf "${XCFW}"

xcodebuild -create-xcframework \
    -library "${BUILD_DIR}/device/Release-iphoneos/libunyts.a" \
    -headers "${SCRIPT_DIR}/../cpp/include" \
    -library "${SIM_LIB_FINAL}" \
    -headers "${SCRIPT_DIR}/../cpp/include" \
    -output "${XCFW}"

echo ""
echo "✓  XCFramework ready at: ${XCFW}"
echo ""
echo "Next steps in Xcode:"
echo "  1. Drag 'build/unyts.xcframework' into your project (Frameworks, Libraries, and Embedded Content)"
echo "  2. Make sure 'unyts_ios-Bridging-Header.h' is set in Build Settings > Swift Compiler - General"
echo "  3. Build & Run on device or simulator"
