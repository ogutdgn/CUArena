find_package(Qt6 REQUIRED COMPONENTS Test)

# QtTest is the harness only; the code under test (mwcore) stays Qt-free.
# AUTOMOC handles the `#include "<name>.moc"` at the bottom of each single-file test.
set(CMAKE_AUTOMOC ON)

# Guiless = headless (QCoreApplication, no display) — matches the distribution image.
function(mw_add_unit_test name)
    add_executable(${name} ${ARGN})
    target_link_libraries(${name} PRIVATE Qt6::Test mwcore)
    add_test(NAME ${name} COMMAND ${name})
endfunction()

mw_add_unit_test(tst_tilegrid unit/tst_tilegrid.cpp)
mw_add_unit_test(tst_tilecache unit/tst_tilecache.cpp)
mw_add_unit_test(tst_rendercontroller unit/tst_rendercontroller.cpp)

# Type-B (headless LOK integration) — only when the engine is built. Plain C++ (no Qt): a
# QCoreApplication conflicts with LibreOffice's own VCL application singleton.
if(MW_HAVE_LOK)
    add_executable(tst_lok_smoke integration/tst_lok_smoke.cpp)
    set_target_properties(tst_lok_smoke PROPERTIES AUTOMOC OFF)
    target_link_libraries(tst_lok_smoke PRIVATE mwengine)
    target_compile_definitions(tst_lok_smoke PRIVATE
        MW_LOK_INSTDIR="${MW_LOK_INSTDIR}"
        MW_FIXTURE_FODT="${CMAKE_CURRENT_SOURCE_DIR}/fixtures/sample.fodt")
    add_test(NAME tst_lok_smoke COMMAND tst_lok_smoke)
    set_tests_properties(tst_lok_smoke PROPERTIES
        ENVIRONMENT "SAL_USE_VCLPLUGIN=svp"
        TIMEOUT 180)
endif()
