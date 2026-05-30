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
