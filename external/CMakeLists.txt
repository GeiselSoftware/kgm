if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Emscripten")
else ()
add_subdirectory(fmt.cmake)
endif()

add_subdirectory(imgui.cmake)
add_subdirectory(imgui-node-editor.cmake)
