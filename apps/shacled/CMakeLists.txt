add_executable(run-shacled run-shacled.cpp rdf-manager.cpp vis-manager.cpp visnode.cpp visnode-userclass.cpp visnode-userobject.cpp)
target_link_libraries(run-shacled lib-apploops lib-utils imgui-node-editor imgui imgui_backends glfw GL fmt)

if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Emscripten")
  target_link_options(run-shacled PUBLIC --shell-file ${CMAKE_CURRENT_SOURCE_DIR}/shell.html --embed-file ${CMAKE_SOURCE_DIR}/fonts@fonts)
else()
  file(COPY ${CMAKE_SOURCE_DIR}/fonts DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
endif()
