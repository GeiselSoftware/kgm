project(lib-apploops)

add_library(${PROJECT_NAME} STATIC loop-runner.cpp)

target_include_directories(${PROJECT_NAME} PUBLIC .. ${IMGUI_ROOT_DIR})
