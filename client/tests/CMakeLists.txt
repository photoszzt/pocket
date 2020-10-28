
set(CMAKE_CXX_FLAGS "-std=c++11 -g")
include_directories(${CMAKE_CURRENT_BINARY_DIR})
include_directories(${PROJECT_SOURCE_DIR})
add_executable(put_del put_del.cc)

TARGET_LINK_LIBRARIES(put_del LINK_PUBLIC cppcrail cpppocket)
install(TARGETS put_del DESTINATION /bin)