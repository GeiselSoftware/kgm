set(_imgui_backends_sources
  ${IMGUI_ROOT_DIR}/backends/imgui_impl_opengl3.cpp
  ${IMGUI_ROOT_DIR}/backends/imgui_impl_glfw.cpp
)

include_directories(${IMGUI_ROOT_DIR})
add_library(imgui_backends STATIC ${_imgui_backends_sources})
