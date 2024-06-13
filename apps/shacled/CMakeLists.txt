add_executable(run-shacled run-shacled.cpp node.cpp node-manager.cpp rdfsclass-node.cpp data-node.cpp)
target_link_libraries(run-shacled lib-apploops lib-utils imgui-node-editor imgui imgui_backends glfw GL)

if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Emscripten")
  target_link_options(run-shacled PUBLIC --shell-file ${CMAKE_CURRENT_SOURCE_DIR}/shell.html --embed-file ${CMAKE_SOURCE_DIR}/fonts@fonts)
else()
  file(COPY ${CMAKE_SOURCE_DIR}/fonts DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
endif()
