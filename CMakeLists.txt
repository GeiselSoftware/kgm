cmake_minimum_required(VERSION 3.12)

project(shacled)

set(NLOHMANN_ROOT_DIR $ENV{HOME}/local/cloned/json)
set(IMGUI_ROOT_DIR $ENV{HOME}/local/cloned/imgui)
set(IMGUI_NODE_EDITOR_ROOT_DIR $ENV{HOME}/local/cloned/imgui-node-editor)

set(CMAKE_BUILD_TYPE Debug)

set(CMAKE_CXX_STANDARD            17)
set(CMAKE_CXX_STANDARD_REQUIRED   YES)

if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Emscripten")
  set(CMAKE_EXECUTABLE_SUFFIX ".html")
  set(CMAKE_CXX_FLAGS "-O2")
  set(CMAKE_EXE_LINKER_FLAGS "-s FETCH=1 -s USE_WEBGL2 -s USE_GLFW=3 -s FULL_ES3=1 -s WASM=1")
else ()
  set(CMAKE_EXECUTABLE_SUFFIX ".tsk")
endif()

add_subdirectory(external)

include_directories(${CMAKE_SOURCE_DIR}/libs ${IMGUI_ROOT_DIR}/backends ${IMGUI_ROOT_DIR} ${IMGUI_NODE_EDITOR_ROOT_DIR} ${NLOHMANN_ROOT_DIR}/include)
add_subdirectory(libs)
add_subdirectory(apps)
