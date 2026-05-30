cmake_minimum_required(VERSION 3.21)

project(msword_clone
    VERSION 0.0.1
    DESCRIPTION "MS Word clone — native Qt6 core renting LibreOffice via LOK (Boundary A)"
    LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build type" FORCE)
endif()

add_compile_options(-Wall -Wextra)

include(CTest)  # defines BUILD_TESTING (default ON) and calls enable_testing()

# --- LibreOfficeKit engine integration (Boundary A) ---
# The engine binding + B/C tests build ONLY when a built LibreOffice instdir is present, so the
# our-layer A-tests still build and run on a machine without the (multi-hour) engine build.
set(MW_LO_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../libreoffice-codebase" CACHE PATH "Vendored LibreOffice tree")
set(MW_LOK_INCLUDE "${MW_LO_DIR}/include")
set(MW_LOK_INSTDIR "${MW_LO_DIR}/instdir/program")
if(EXISTS "${MW_LOK_INSTDIR}/libsofficeapp.so" AND EXISTS "${MW_LOK_INCLUDE}/LibreOfficeKit/LibreOfficeKit.hxx")
    set(MW_HAVE_LOK ON)
    message(STATUS "LOK engine found (${MW_LOK_INSTDIR}) — building engine binding + B/C tests")
else()
    set(MW_HAVE_LOK OFF)
    message(STATUS "LOK engine not built — engine binding + B/C tests skipped (A-tests only)")
endif()

add_subdirectory(src)

if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
