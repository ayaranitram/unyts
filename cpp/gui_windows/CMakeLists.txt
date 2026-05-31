cmake_minimum_required(VERSION 3.15)
project(unyts_gui_windows VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Automoc/autouic/autorcc for Qt
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# ─── Qt 6 ─────────────────────────────────────────────────────────────────────
find_package(Qt6 REQUIRED COMPONENTS Core Widgets)

# ─── unyts core (re-compiled with MinGW for ABI compatibility) ────────────────
# Point to the shared C++ sources; we compile them again under MinGW so the
# GUI and the core share the same runtime, avoiding MSVC/MinGW ABI mismatch.
set(UNYTS_SRC_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/../src")
set(UNYTS_INC_DIR  "${CMAKE_CURRENT_SOURCE_DIR}/../include")

set(UNYTS_CACHE_SCHEMA_VERSION 1)

add_library(unyts_core_mingw STATIC
    ${UNYTS_SRC_DIR}/graph.cpp
    ${UNYTS_SRC_DIR}/aliases.cpp
    ${UNYTS_SRC_DIR}/binary_cache.cpp
    ${UNYTS_SRC_DIR}/converter.cpp
    ${UNYTS_SRC_DIR}/conversions.cpp
    ${UNYTS_SRC_DIR}/database.cpp
    ${UNYTS_SRC_DIR}/parser.cpp
)
target_include_directories(unyts_core_mingw PUBLIC ${UNYTS_INC_DIR})
target_compile_definitions(unyts_core_mingw PRIVATE
    UNYTS_CACHE_SCHEMA_VERSION=${UNYTS_CACHE_SCHEMA_VERSION}
)
target_compile_options(unyts_core_mingw PRIVATE -Wall -Wextra -O2)

# ─── GUI application ──────────────────────────────────────────────────────────
qt_add_executable(unyts_gui
    main.cpp
    MainWindow.cpp
    MainWindow.h
    resources.qrc       # Qt resource — embeds icon for runtime use
    app.rc              # Windows resource — sets EXE file icon
)
target_link_libraries(unyts_gui PRIVATE
    Qt6::Core
    Qt6::Widgets
    unyts_core_mingw
)
target_compile_options(unyts_gui PRIVATE -Wall -Wextra -O2)

# Windows: set subsystem to GUI (no console window)
if(WIN32)
    set_target_properties(unyts_gui PROPERTIES WIN32_EXECUTABLE TRUE)
endif()

# ─── Install ──────────────────────────────────────────────────────────────────
install(TARGETS unyts_gui DESTINATION bin)
