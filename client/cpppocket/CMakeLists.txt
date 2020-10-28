set(CMAKE_CXX_FLAGS "-fPIC -std=c++14 -g")
include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include_directories(${CMAKE_CURRENT_BINARY_DIR})
include_directories(${PROJECT_SOURCE_DIR})
add_library(cpppocket SHARED cpppocket_dispatcher.cc)
target_link_libraries(cpppocket cppcrail)
install(TARGETS cpppocket DESTINATION /lib)
install (FILES
	cpppocket_dispatcher.h
	DESTINATION /include)
