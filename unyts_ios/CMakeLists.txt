cmake_minimum_required(VERSION 3.21)
project(libunyts VERSION 1.0.0 LANGUAGES CXX)

# ── Sources ───────────────────────────────────────────────────────────────────
# The C++ core and C API live in the repo root's cpp/ directory.
set(CPP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../cpp")

file(GLOB UNYTS_CORE_SRC "${CPP_ROOT}/src/*.cpp")

# Build a static library consumed by the Xcode project via XCFramework.
add_library(unyts STATIC
    ${UNYTS_CORE_SRC}
    "${CPP_ROOT}/capi/unyts_capi.cpp"
)

target_include_directories(unyts PUBLIC "${CPP_ROOT}/include")
target_compile_features(unyts PUBLIC cxx_std_17)
target_compile_options(unyts PRIVATE -fexceptions -frtti -Wall -Wextra -Wno-unused-parameter)

set_target_properties(unyts PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

# ── Build instructions ────────────────────────────────────────────────────────
# Run from the repo root on a macOS machine:
#
#   # Device (arm64)
#   cmake -S unyts_ios -B unyts_ios/build_ios_device \
#     -DCMAKE_SYSTEM_NAME=iOS \
#     -DCMAKE_OSX_ARCHITECTURES=arm64 \
#     -DCMAKE_OSX_DEPLOYMENT_TARGET=16.0 \
#     -DCMAKE_BUILD_TYPE=Release
#   cmake --build unyts_ios/build_ios_device
#
#   # Simulator (arm64 + x86_64)
#   cmake -S unyts_ios -B unyts_ios/build_ios_sim \
#     -DCMAKE_SYSTEM_NAME=iOS \
#     -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" \
#     -DCMAKE_OSX_SYSROOT=iphonesimulator \
#     -DCMAKE_OSX_DEPLOYMENT_TARGET=16.0 \
#     -DCMAKE_BUILD_TYPE=Release
#   cmake --build unyts_ios/build_ios_sim
#
#   # Package as XCFramework
#   xcodebuild -create-xcframework \
#     -library unyts_ios/build_ios_device/lib/libunyts.a \
#     -library unyts_ios/build_ios_sim/lib/libunyts.a \
#     -output unyts_ios/UnytsCore.xcframework
