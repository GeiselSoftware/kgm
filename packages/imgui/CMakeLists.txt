project(imgui VERSION 1.76)

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

add_library(${PROJECT_NAME} STATIC ${_imgui_Sources})

target_include_directories(${PROJECT_NAME} PUBLIC ${IMGUI_ROOT_DIR})
