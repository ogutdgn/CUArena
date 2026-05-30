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

add_subdirectory(src)

if(BUILD_TESTING)
    add_subdirectory(tests)
endif()
