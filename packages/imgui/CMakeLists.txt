project(imgui VERSION 1.76)

include_directories(${PROJECT_NAME} PUBLIC ${IMGUI_ROOT_DIR})

set(_imgui_Sources
    ${IMGUI_ROOT_DIR}/imconfig.h
    ${IMGUI_ROOT_DIR}/imgui.cpp
    ${IMGUI_ROOT_DIR}/imgui.h
    ${IMGUI_ROOT_DIR}/imgui_demo.cpp
    ${IMGUI_ROOT_DIR}/imgui_draw.cpp
    ${IMGUI_ROOT_DIR}/imgui_internal.h
    ${IMGUI_ROOT_DIR}/imgui_widgets.cpp
    ${IMGUI_ROOT_DIR}/imgui_tables.cpp
    ${IMGUI_ROOT_DIR}/imstb_rectpack.h
    ${IMGUI_ROOT_DIR}/imstb_textedit.h
    ${IMGUI_ROOT_DIR}/imstb_truetype.h
    ${IMGUI_ROOT_DIR}/misc/cpp/imgui_stdlib.cpp
    ${IMGUI_ROOT_DIR}/LICENSE.txt
)

add_library(imgui STATIC ${_imgui_Sources})

set(_imgui_backends_sources
  ${IMGUI_ROOT_DIR}/backends/imgui_impl_opengl3.cpp
  ${IMGUI_ROOT_DIR}/backends/imgui_impl_glfw.cpp
)

add_library(imgui_backends STATIC ${_imgui_backends_sources})
