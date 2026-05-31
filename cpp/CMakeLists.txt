cmake_minimum_required(VERSION 3.15)
project(unyts_cpp VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ─── Cache schema version ─────────────────────────────────────────────────────
set(UNYTS_CACHE_SCHEMA_VERSION 1)

# ─── Core static library ──────────────────────────────────────────────────────
add_library(unyts_core STATIC
    src/graph.cpp
    src/aliases.cpp
    src/binary_cache.cpp
    src/converter.cpp
    src/conversions.cpp
    src/database.cpp
    src/parser.cpp
)
target_include_directories(unyts_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_definitions(unyts_core PRIVATE
    UNYTS_CACHE_SCHEMA_VERSION=${UNYTS_CACHE_SCHEMA_VERSION}
)
if(MSVC)
    target_compile_options(unyts_core PRIVATE /W3 /bigobj /EHsc)
else()
    target_compile_options(unyts_core PRIVATE -Wall -Wextra)
endif()

# ─── Python / pybind11 bindings ───────────────────────────────────────────────
# Prefer the pybind11 installed in the project's .venv, then fall back to the
# system install.  Set PYBIND11_DIR on the cmake command line to override.
if(NOT DEFINED PYBIND11_DIR)
    set(PYBIND11_DIR
        "${CMAKE_CURRENT_SOURCE_DIR}/../.venv/Lib/site-packages/pybind11"
        CACHE PATH "Path to pybind11 cmake config directory")
endif()

find_package(pybind11 CONFIG
    PATHS "${PYBIND11_DIR}" "${PYBIND11_DIR}/share/cmake/pybind11"
    NO_DEFAULT_PATH
    QUIET
)
if(NOT pybind11_FOUND)
    # Second attempt: standard search paths
    find_package(pybind11 CONFIG REQUIRED)
endif()

pybind11_add_module(unyts_cpp_native MODULE python/bindings.cpp)
target_link_libraries(unyts_cpp_native PRIVATE unyts_core)
target_compile_definitions(unyts_cpp_native PRIVATE
    UNYTS_CACHE_SCHEMA_VERSION=${UNYTS_CACHE_SCHEMA_VERSION}
)
if(MSVC)
    target_compile_options(unyts_cpp_native PRIVATE /bigobj /EHsc)
endif()

# ─── C API shared library ─────────────────────────────────────────────────────
add_library(unyts_capi SHARED capi/unyts_capi.cpp)
target_link_libraries(unyts_capi PRIVATE unyts_core)
target_include_directories(unyts_capi PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_definitions(unyts_capi PRIVATE
    UNYTS_CAPI_BUILDING_DLL
    UNYTS_CACHE_SCHEMA_VERSION=${UNYTS_CACHE_SCHEMA_VERSION}
)
if(MSVC)
    target_compile_options(unyts_capi PRIVATE /W3 /EHsc)
    # Export all symbols defined with UNYTS_API; the rest stay hidden.
    set_target_properties(unyts_capi PROPERTIES
        WINDOWS_EXPORT_ALL_SYMBOLS OFF)
else()
    target_compile_options(unyts_capi PRIVATE -Wall -Wextra -fvisibility=hidden)
endif()

# ─── Install rules ────────────────────────────────────────────────────────────
install(TARGETS unyts_core ARCHIVE DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
install(TARGETS unyts_cpp_native DESTINATION bin)
install(TARGETS unyts_capi
    RUNTIME DESTINATION bin      # .dll on Windows
    LIBRARY DESTINATION lib      # .so on Linux/macOS
    ARCHIVE DESTINATION lib)     # .lib import lib on Windows

# ─── C++ test suite ───────────────────────────────────────────────────────────
enable_testing()

add_executable(unyts_tests tests/test_core.cpp)
target_link_libraries(unyts_tests PRIVATE unyts_core unyts_capi)
target_include_directories(unyts_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_compile_definitions(unyts_tests PRIVATE
    UNYTS_CACHE_SCHEMA_VERSION=${UNYTS_CACHE_SCHEMA_VERSION}
)
if(MSVC)
    target_compile_options(unyts_tests PRIVATE /W3 /EHsc /bigobj)
else()
    target_compile_options(unyts_tests PRIVATE -Wall -Wextra)
endif()

add_test(NAME core_tests COMMAND unyts_tests)
set_tests_properties(core_tests PROPERTIES TIMEOUT 60)
