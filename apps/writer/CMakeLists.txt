cmake_minimum_required(VERSION 3.21)
project(writer VERSION 0.1 LANGUAGES CXX)

# Modern native Qt6 Word-like CUA Writer app. Drives the LibreOffice engine
# headlessly via LibreOfficeKit (see docs/architecture/ARCHITECTURE.md).
# W2: shell + LOK binding. The LOK engine path is provided at configure time.

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Qml Quick QuickControls2 Svg)

# Path to the built engine tree (for the LOK headers + runtime install dir).
# Default assumes the in-repo engine; override with -DWRITER_ENGINE_DIR=...
set(WRITER_ENGINE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../libreoffice/libreoffice-codebase"
    CACHE PATH "LibreOffice engine source tree (provides include/LibreOfficeKit + instdir)")

qt_add_executable(writer
    src/main.cpp
)

qt_add_resources(writer "app_qml"
    PREFIX "/"
    FILES
        src/ui/qml/Main.qml
)

target_include_directories(writer PRIVATE
    "${WRITER_ENGINE_DIR}/include"   # LibreOfficeKit/*.h (header-only client)
)

target_compile_definitions(writer PRIVATE
    LOK_USE_UNSTABLE_API             # unlock paintTile/postUnoCommand/... in the LOK header
    WRITER_ENGINE_INSTALL="${WRITER_ENGINE_DIR}/instdir/program"
)

target_link_libraries(writer PRIVATE
    Qt6::Core Qt6::Gui Qt6::Qml Qt6::Quick Qt6::QuickControls2 Qt6::Svg
    ${CMAKE_DL_LIBS}                 # dlopen for lok_init at runtime
)
