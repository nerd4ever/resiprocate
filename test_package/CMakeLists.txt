cmake_minimum_required(VERSION 3.1)
if (POLICY CMP0091)
    cmake_policy(SET CMP0091 NEW)
endif ()

project(example CXX)

#set(RESIP_COMPONENTS rutil resipmedia resip dum resipares)
#
#foreach(COMP ${RESIP_COMPONENTS})
#    find_package(${COMP} REQUIRED)
#    include_directories(${${COMP}_INCLUDE_DIRS})
#    list(APPEND example-deps ${${COMP}_LIBRARIES})
#endforeach()
#
#find_package(resiprocate CONFIG REQUIRED COMPONENTS rutil resipmedia resip dum resipares)
find_package(resiprocate REQUIRED)
include_directories(${resiprocate_INCLUDE_DIRS})
list(APPEND example-deps ${resiprocate_LIBRARIES})


add_executable(${PROJECT_NAME} src/example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${example-deps})
message("example dependencies => ${example-deps}")
