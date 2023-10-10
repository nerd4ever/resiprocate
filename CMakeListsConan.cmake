cmake_minimum_required(VERSION 3.12 FATAL_ERROR)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/build/cmake_modules")
if (POLICY CMP0091)
    cmake_policy(SET CMP0091 NEW)
endif ()
if (POLICY CMP0042)
    CMAKE_POLICY(SET CMP0042 NEW)
endif (POLICY CMP0042)
if (POLICY CMP0077)
    CMAKE_POLICY(SET CMP0077 NEW)
endif (POLICY CMP0077)

project(resiprocate VERSION 1.12.1)
if (NOT WIN32)
    find_package(PkgConfig REQUIRED)
endif ()

# set(SO_ABI "0.0.0")
# set(SO_RELEASE "${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}")

include(GNUInstallDirs)
include(Utilities)
include(CheckStructHasMember)

if (ENABLE_TEST)
    enable_testing()
endif ()

# POPT ------------------------------------------
if(USE_POPT)
    find_package(popt REQUIRED)
    set(HAVE_POPT_H true)
    add_definitions(-DHAVE_POPT_H)
endif()

# https://cmake.org/cmake/help/latest/module/FindThreads.html
set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
find_package(Threads REQUIRED)

if (CMAKE_USE_PTHREADS_INIT)
    add_definitions(-D__REENTRANT)
    add_definitions(-pthread)
endif ()

set(REPRO_BUILD_REV ${PACKAGE_VERSION})
set(REPRO_RELEASE_VERSION ${PACKAGE_VERSION})
set(RESIP_SIP_MSG_MAX_BYTES 10485760)

# https://cmake.org/cmake/help/latest/module/TestBigEndian.html
# see also
# https://cmake.org/cmake/help/latest/variable/CMAKE_LANG_BYTE_ORDER.html
include(TestBigEndian)
test_big_endian(RESIP_BIG_ENDIAN)

CHECK_STRUCT_HAS_MEMBER(sockaddr_in sin_len arpa/inet.h HAVE_sockaddr_in_len)
if (HAVE_sockaddr_in_len)
    add_definitions(-DHAVE_sockaddr_in_len)
endif ()

# Top-level user-settable variables (with defaults)
# Those can be queried from the command line using "cmake -LH" and can be
# specified on the command line, using cmake-gui or ccmake.
option(VERSIONED_SONAME "Include Major.Minor version in SONAME" FALSE)
option(USE_IPV6 "Enable IPv6" TRUE)
option(USE_DTLS "Enable DTLS" TRUE)
option(PEDANTIC_STACK "Enable pedantic behavior (fully parse all messages)" FALSE)
option(BUILD_DSO_PLUGINS "Build DSO plugins" TRUE)
option(USE_LIBWEBRTC "Link against LibWebRTC" FALSE)
option(RESIP_ASSERT_SYSLOG "Log assertion failures with Syslog" FALSE)

set(DEFAULT_BRIDGE_MAX_IN_OUTPUTS 20 CACHE STRING "recon: Maximum connections on bridge")

# This must be enabled when building with the Android ndkports tools.
# It should not be enabled for any other case.
option(USE_NDKPORTS_HACKS "Android ndkports build: use hardcoded paths to dependencies" FALSE)

set(CMAKE_CXX_STANDARD 11)

########################
### Helper functions ###
########################

function(option_def)
    if (${ARGV0})
        add_definitions(-D${ARGV0})
    endif ()
endfunction()

function(set_def)
    set(${ARGV0} TRUE)
    add_definitions(-D${ARGV0})
endfunction()

function(do_fail_win32)
    message(FATAL_ERROR "please complete Win32 support for ${ARGV0} in CMakeLists.txt")
endfunction()

# See
#   https://cmake.org/cmake/help/latest/prop_tgt/SOVERSION.html
#   https://cmake.org/cmake/help/latest/prop_tgt/VERSION.html
function(version_libname)
    if (SO_ABI)
        set_target_properties(${ARGV0} PROPERTIES SOVERSION ${SO_ABI})
    endif ()
    # This logic tries to replicate the libtool -release X.Y ...
    # but it doesn't create the same symlink that libtool creates.
    # FIXME
    # Other people have complained about the same problem, e.g.
    # https://discourse.libsdl.org/t/patches-dynamic-library-name-should-it-be-libsdl2-2-0-so-or-libsdl2-so/19400/8
    if (VERSIONED_SONAME)
        set_target_properties(${ARGV0} PROPERTIES OUTPUT_NAME ${ARGV0}-${SO_RELEASE})
        file(CREATE_LINK lib${ARGV0}-${SO_RELEASE}.so ${CMAKE_CURRENT_BINARY_DIR}/lib${ARGV0}.so RESULT ${ARGV0}-IGNORE SYMBOLIC)
        install(FILES ${CMAKE_CURRENT_BINARY_DIR}/lib${ARGV0}.so DESTINATION ${CMAKE_INSTALL_LIBDIR})
    endif ()
endfunction()

if (NOT VERSIONED_SONAME)
    set(CMAKE_PLATFORM_NO_VERSIONED_SONAME True)
endif ()

################################
### Per-program dependencies ###
################################

set(USE_PCRE FALSE)
if ("${CMAKE_EXE_LINKER_FLAGS}" STREQUAL "/machine:x64")
    set(WIN_ARCH "x64")
else ()
    set(WIN_ARCH "Win32")
endif ()
# C-ARES ----------------------------------------
add_definitions(-DUSE_CARES)
find_package(c-ares REQUIRED)
set(ARES_LIBRARIES ${c-ares_LIBRARIES})
include_directories(${c-ares_INCLUDE_DIRS})
link_directories(${c-ares_LIBRARY_DIRS})
set(USE_CARES true)
# OpenSSL ---------------------------------------
find_package(OpenSSL REQUIRED) # HINTS ${OPENSSL_LIBRARIES})
# Oldest OpenSSL API to target (1.1.1)
add_compile_definitions(OPENSSL_API_COMPAT=0x10101000L)
set_def(USE_SSL)


option_def(USE_IPV6)
option_def(USE_DTLS)
option_def(PEDANTIC_STACK)

if (USE_MAXMIND_GEOIP)
    find_package(maxminddb REQUIRED)
endif ()

set(CMAKE_INSTALL_PKGLIBDIR ${CMAKE_INSTALL_LIBDIR}/${CMAKE_PROJECT_NAME})

if (BUILD_DSO_PLUGINS)
    add_definitions(-DDSO_PLUGINS)
    set(INSTALL_REPRO_PLUGIN_DIR ${CMAKE_INSTALL_PKGLIBDIR}/repro/plugins)
endif ()

find_package(libsrtp REQUIRED)
option_def(USE_LIBWEBRTC)
option_def(RESIP_ASSERT_SYSLOG)

include(CheckCSourceRuns)

check_c_source_runs("
   #include <time.h>
   int main() {
      struct timespec ts;
      clock_gettime(CLOCK_MONOTONIC, &ts);
      return 0;
   }" HAVE_CLOCK_GETTIME_MONOTONIC)

if (HAVE_CLOCK_GETTIME_MONOTONIC)
    add_definitions(-DHAVE_CLOCK_GETTIME_MONOTONIC)
endif ()

# epoll
include(CheckIncludeFiles)
check_include_files(sys/epoll.h HAVE_EPOLL)

# HAVE_LIBDL from autotools obsolete,
# now we use CMAKE_DL_LIBS to include the library
# when necessary

# gperf
set(GPERF_SIZE_TYPE "size_t")

if (WIN32)
    add_definitions(-DNOMINMAX)
endif ()

##############################
### Generation of config.h ###
##############################
# TODO - Bring more values from autotools
add_definitions(-DHAVE_CONFIG_H)
configure_file(config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/config.h)
include_directories(${CMAKE_CURRENT_BINARY_DIR})

# Used to group targets together when CMake generates projects for IDEs
set_property(GLOBAL PROPERTY USE_FOLDERS ON)
# Resiprocate Library rutil ----------------------------------------
add_subdirectory(rutil)
# Resiprocate Library resip ----------------------------------------
add_subdirectory(resip)
if (REGENERATE_MEDIA_SAMPLES)
    find_package(soxr REQUIRED)
endif ()
add_subdirectory(media)

# add_subdirectory(apps)

# Create spec file for RPM packaging
# The tarball containing a spec file can be fed directly
# to the rpmbuild command.
configure_file(
        resiprocate.spec.in
        resiprocate.spec
        @ONLY)

# Add 'make dist' command for creating release tarball
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_SOURCE_GENERATOR "TGZ")
set(CPACK_SOURCE_PACKAGE_FILE_NAME "${CMAKE_PROJECT_NAME}-${CPACK_PACKAGE_VERSION}")

# pax appears to be the default, we need it due to some filenames
#set (COMPRESSION_OPTIONS --format=pax)

list(APPEND CPACK_SOURCE_IGNORE_FILES "/\\\\.git/")
list(APPEND CPACK_SOURCE_IGNORE_FILES ".gitignore")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/CMakeFiles/")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/_CPack_Packages/")
list(APPEND CPACK_SOURCE_IGNORE_FILES "\\\\.deps/")
list(APPEND CPACK_SOURCE_IGNORE_FILES "\\\\.libs/")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/.*\\\\.gz")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/.*\\\\.zip")
list(APPEND CPACK_SOURCE_IGNORE_FILES ".*\\\\.o")
list(APPEND CPACK_SOURCE_IGNORE_FILES "lib.*\\\\.so*")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/CMakeCache.txt")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/contrib")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/debian")
list(APPEND CPACK_SOURCE_IGNORE_FILES "Makefile")
list(APPEND CPACK_SOURCE_IGNORE_FILES "/config.h$")

include(CPack)
add_custom_target(dist COMMAND ${CMAKE_MAKE_PROGRAM} package_source)

###############
### Summary ###
###############

include(FeatureSummary)
feature_summary(WHAT ALL)