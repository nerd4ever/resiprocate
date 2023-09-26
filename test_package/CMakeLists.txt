cmake_minimum_required(VERSION 3.1)
if (POLICY CMP0091)
    cmake_policy(SET CMP0091 NEW)
endif ()

project(example CXX)

find_package(dum CONFIG REQUIRED)
include_directories(${dum_INCLUDE_DIRS})
list(APPEND example-deps ${dum_LIBRARIES})


find_package(resip CONFIG REQUIRED)
include_directories(${resip_INCLUDE_DIRS})
list(APPEND example-deps ${resip_LIBRARIES})


find_package(resipares CONFIG REQUIRED)
include_directories(${resipares_INCLUDE_DIRS})
list(APPEND example-deps ${resipares_LIBRARIES})

find_package(resipmedia CONFIG REQUIRED)
include_directories(${resipmedia_INCLUDE_DIRS})
list(APPEND example-deps ${resipmedia_LIBRARIES})

find_package(rutil CONFIG REQUIRED)
include_directories(${rutil_INCLUDE_DIRS})
list(APPEND example-deps ${rutil_LIBRARIES})

find_package(sipdial CONFIG REQUIRED)
include_directories(${sipdial_INCLUDE_DIRS})
list(APPEND example-deps ${sipdial_LIBRARIES})


add_executable(${PROJECT_NAME} src/example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${example-deps})
message("example dependencies => ${example-deps}")
