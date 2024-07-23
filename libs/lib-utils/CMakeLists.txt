project(lib-utils)

file(GLOB_RECURSE sources CONFIGURE_DEPENDS "*.cpp")

add_library(${PROJECT_NAME} STATIC ${sources})

#target_include_directories(${PROJECT_NAME} PUBLIC .. ${IMGUI_ROOT_DIR})
