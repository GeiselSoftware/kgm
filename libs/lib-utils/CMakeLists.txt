project(lib-utils)

add_library(${PROJECT_NAME} STATIC rdf-utils.cpp fuseki-utils.cpp http-utils.cpp uuid.cpp)

#target_include_directories(${PROJECT_NAME} PUBLIC .. ${IMGUI_ROOT_DIR})
