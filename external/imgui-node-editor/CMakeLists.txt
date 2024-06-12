project(imgui-node-editor)

set(_imgui_node_editor_Sources
  ${IMGUI_NODE_EDITOR_ROOT_DIR}/imgui_node_editor.cpp
  ${IMGUI_NODE_EDITOR_ROOT_DIR}/imgui_node_editor_api.cpp
  ${IMGUI_NODE_EDITOR_ROOT_DIR}/imgui_canvas.cpp
  ${IMGUI_NODE_EDITOR_ROOT_DIR}/crude_json.cpp
)

add_library(${PROJECT_NAME} STATIC ${_imgui_node_editor_Sources})

target_include_directories(${PROJECT_NAME} PUBLIC ${IMGUI_ROOT_DIR})
