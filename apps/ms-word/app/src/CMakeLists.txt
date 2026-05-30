# mwcore — the our-layer core (above Boundary A).
#
# Plain C++: NO Qt, NO LOK. This is the toolkit- and engine-independent logic —
# tile geometry, dispatch routing, the document/state model. The engine binding
# that actually calls LOK is a separate target added later, guarded on the LOK build,
# so this library and its tests build and run with no engine present.
add_library(mwcore STATIC
    core/TileGrid.cpp
    core/TileCache.cpp
    core/RenderController.cpp
)
target_include_directories(mwcore PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_features(mwcore PUBLIC cxx_std_20)
