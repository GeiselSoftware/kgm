project(lib-utils)

add_library(${PROJECT_NAME} STATIC http-utils.cpp fuseki-utils.cpp uuid.cpp)

#target_include_directories(${PROJECT_NAME} PUBLIC .. ${IMGUI_ROOT_DIR})
