project(fmt)

set(_fmt_Sources
  #${FMT_ROOT_DIR}/src/fmt.cc
  ${FMT_ROOT_DIR}/src/format.cc
  ${FMT_ROOT_DIR}/src/os.cc
)

add_library(${PROJECT_NAME} STATIC ${_fmt_Sources})

target_include_directories(${PROJECT_NAME} PUBLIC ${FMT_ROOT_DIR}/include)
