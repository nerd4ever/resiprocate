# Try to find BerkeleyDb.
#
# Adapted from the CMake wiki page
#
# http://www.cmake.org/Wiki/CMake:How_To_Find_Libraries
#
# Once done this will define
#
#  BERKELEYDB_FOUND - System has BerkeleyDb
#  BERKELEYDB_INCLUDE_DIRS - The BerkeleyDb include directories
#  BERKELEYDB_LIBRARIES - The libraries needed to use BerkeleyDb
#  BERKELEYDB_DEFINITIONS - Compiler switches required for using BerkeleyDb

# If pkg-config is present, use its results as hints for FIND_*, otherwise
# don't
FIND_PACKAGE(PkgConfig)
PKG_CHECK_MODULES(PC_BERKELEYDB QUIET libdb)
SET(BERKELEYDB_DEFINITIONS ${PC_BERKELEYDB_CFLAGS_OTHER})

FIND_PATH(BERKELEYDB_INCLUDE_DIR db_cxx.h
          HINTS ${PC_BERKELEYDB_INCLUDEDIR} ${PC_BERKELEYDB_INCLUDE_DIRS})

FIND_LIBRARY(BERKELEYDB_LIBRARY_DB NAMES db
             HINTS ${PC_BERKELEYDB_LIBDIR} ${PC_BERKELEYDB_LIBRARY_DIRS})

FIND_LIBRARY(BERKELEYDB_LIBRARY_CXX NAMES db_cxx
             HINTS ${PC_BERKELEYDB_LIBDIR} ${PC_BERKELEYDB_LIBRARY_DIRS})

SET(BERKELEYDB_LIBRARIES ${BERKELEYDB_LIBRARY_DB} ${BERKELEYDB_LIBRARY_CXX})
SET(BERKELEYDB_INCLUDE_DIRS ${BERKELEYDB_INCLUDE_DIR})

INCLUDE(FindPackageHandleStandardArgs)

FIND_PACKAGE_HANDLE_STANDARD_ARGS(BerkeleyDb DEFAULT_MSG
                                  BERKELEYDB_LIBRARY_DB BERKELEYDB_LIBRARY_CXX BERKELEYDB_INCLUDE_DIR)

MARK_AS_ADVANCED(BERKELEYDB_INCLUDE_DIR BERKELEYDB_LIBRARY_DB BERKELEYDB_LIBRARY_CXX)