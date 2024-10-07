file(GLOB_RECURSE sources CONFIGURE_DEPENDS "*.cpp")

add_executable(run-shacled ${sources})

if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Emscripten")
target_link_libraries(run-shacled lib-apploops lib-utils imgui-node-editor imgui imgui_backends glfw GL)
else ()
target_link_libraries(run-shacled lib-apploops lib-utils imgui-node-editor imgui imgui_backends glfw GL fmt)
endif()

if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Emscripten")
  target_link_options(run-shacled PUBLIC --shell-file ${CMAKE_CURRENT_SOURCE_DIR}/shell.html --embed-file ${CMAKE_SOURCE_DIR}/libs/wasm-resources@.)
endif()
