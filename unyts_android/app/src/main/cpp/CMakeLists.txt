cmake_minimum_required(VERSION 3.22.1)
project(unyts_jni)

# Repo root — this file is at unyts_android/app/src/main/cpp/CMakeLists.txt
# so going up 5 directories reaches the repo root.
set(REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../..")

# Collect all C++ core source files.
file(GLOB UNYTS_CORE_SRC "${REPO_ROOT}/cpp/src/*.cpp")

# Build the JNI bridge as a single shared library that includes the C++ core
# and the C API implementation — no separate .so dependency needed.
add_library(unyts_jni SHARED
    unyts_jni.cpp
    "${REPO_ROOT}/cpp/capi/unyts_capi.cpp"
    ${UNYTS_CORE_SRC}
)

target_include_directories(unyts_jni PRIVATE
    "${REPO_ROOT}/cpp/include"
)

target_compile_options(unyts_jni PRIVATE
    -std=c++17
    -fexceptions
    -frtti
    -Wall
    -Wextra
    -Wno-unused-parameter
)

# Export all symbols so the JNI runtime can resolve Java_... entry points.
target_link_options(unyts_jni PRIVATE -Wl,--export-dynamic)

find_library(log-lib log)

target_link_libraries(unyts_jni
    android
    ${log-lib}
)
