cmake_minimum_required(VERSION 3.15)
project(nearest_cpp)

include(ExternalProject)
include(FetchContent)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Release)

# --- Python headers ---
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(nanobind REQUIRED)


# --- Main module ---
nanobind_add_module(
  # Name of the extension
  nearest_cpp

  # Target the stable ABI for Python 3.12+, which reduces
  # the number of binary wheels that must be built. This
  # does nothing on older Python versions
  STABLE_ABI

  # Build libnanobind statically and merge it into the
  # extension (which itself remains a shared library)
  #
  # If your project builds multiple extensions, you can
  # replace this flag by NB_SHARED to conserve space by
  # reusing a shared libnanobind across libraries
  NB_STATIC

  # Source code goes here
  nearest_cpp.cpp
)

# --- Install ---
install(TARGETS nearest_cpp
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
) 