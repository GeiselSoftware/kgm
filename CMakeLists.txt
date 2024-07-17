cmake_minimum_required(VERSION 3.12)

project(KGM)

# check src-packages/README.md to find out how to setup env vars used below
#
set(FMT_ROOT_DIR $ENV{FMT_ROOT_DIR})
set(NLOHMANN_ROOT_DIR $ENV{NLOHMANN_ROOT_DIR})
set(IMGUI_ROOT_DIR $ENV{IMGUI_ROOT_DIR})
set(IMGUI_NODE_EDITOR_ROOT_DIR $ENV{IMGUI_NODE_EDITOR_ROOT_DIR})

#set(CMAKE_BUILD_TYPE Debug)

set(CMAKE_CXX_STANDARD            20)
set(CMAKE_CXX_STANDARD_REQUIRED   YES)

if ("${CMAKE_SYSTEM_NAME}" STREQUAL "Emscripten")
  set(CMAKE_EXECUTABLE_SUFFIX ".html")
  set(CMAKE_CXX_FLAGS "-fsanitize=undefined -sNO_DISABLE_EXCEPTION_CATCHING -gsource-map") # -g") # -O2")
  set(CMAKE_EXE_LINKER_FLAGS "--emrun -s FETCH=1 -s USE_WEBGL2 -s USE_GLFW=3 -s FULL_ES3=1 -s WASM=1")
else ()
  set(CMAKE_EXECUTABLE_SUFFIX ".tsk")
endif()

add_subdirectory(src-packages)

include_directories(${CMAKE_SOURCE_DIR}/libs ${IMGUI_ROOT_DIR}/backends ${IMGUI_ROOT_DIR} ${IMGUI_NODE_EDITOR_ROOT_DIR} ${NLOHMANN_ROOT_DIR}/include ${FMT_ROOT_DIR}/include)
add_subdirectory(libs)
add_subdirectory(apps)
