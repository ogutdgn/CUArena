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

# mwengine — the LOK engine binding (the ONLY code that calls LibreOfficeKit). Built only when
# the engine instdir exists. Links libdl for the dlopen/dlsym init + pump-symbol resolution.
if(MW_HAVE_LOK)
    add_library(mwengine STATIC engine/LokEngine.cpp)
    target_include_directories(mwengine PUBLIC ${CMAKE_CURRENT_SOURCE_DIR} ${MW_LOK_INCLUDE})
    target_compile_definitions(mwengine PRIVATE LOK_USE_UNSTABLE_API)
    target_compile_features(mwengine PUBLIC cxx_std_20)
    target_link_libraries(mwengine PUBLIC mwcore ${CMAKE_DL_LIBS})
endif()
