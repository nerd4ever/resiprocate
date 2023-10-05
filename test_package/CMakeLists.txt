cmake_minimum_required(VERSION 3.12)
if (POLICY CMP0091)
    cmake_policy(SET CMP0091 NEW)
endif ()

project(example CXX)

add_executable(${PROJECT_NAME} src/example.cpp)
find_package(resiprocate REQUIRED COMPONENTS rutil resip dum resipares resipmedia)
list(APPEND example-deps resiprocate::resiprocate)
target_include_directories(${PROJECT_NAME} PRIVATE ${resiprocate_INCLUDE_DIRS})

find_package(OpenSSL REQUIRED)
list(APPEND example-deps ${OpenSSL_LIBRARIES})
target_include_directories(${PROJECT_NAME} PRIVATE ${OpenSSL_INCLUDE_DIRS})

find_package(c-ares REQUIRED)
list(APPEND example-deps ${c-ares_LIBRARIES})
target_include_directories(${PROJECT_NAME} PRIVATE ${OpenSSL_INCLUDE_DIRS})

target_link_libraries(${PROJECT_NAME} PRIVATE ${example-deps})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

message("example dependencies => ${example-deps}")
