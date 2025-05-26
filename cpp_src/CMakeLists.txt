cmake_minimum_required(VERSION 3.15)
project(fintechx_core CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenSSL
find_package(OpenSSL REQUIRED)

# Define the core library sources
set(CORE_SOURCES
    src/pan_utils.cpp
    src/encryption_utils.cpp
    # Add other core C++ source files here
)

# Define the core library headers (optional, but good practice)
set(CORE_HEADERS
    include/fintechx_core/pan_utils.hpp
    include/fintechx_core/encryption_utils.hpp
    # Add other core C++ header files here
)

# Add the core library (can be STATIC or SHARED)
# Using STATIC here as it will be linked into the Python extension module
add_library(fintechx_core STATIC ${CORE_SOURCES} ${CORE_HEADERS})

target_include_directories(fintechx_core PUBLIC include)

# Link core library against OpenSSL
target_link_libraries(fintechx_core PRIVATE OpenSSL::SSL OpenSSL::Crypto)

# --- Pybind11 Integration ---
# Find pybind11 package (requires pybind11 to be installed, e.g., via pip)
find_package(pybind11 CONFIG REQUIRED)

# Define the Python binding module sources
set(BINDING_SOURCES
    src/bindings.cpp
)

# Create the Python extension module
# The first argument is the name of the module as it will be imported in Python
pybind11_add_module(fintechx_native ${BINDING_SOURCES})

# Link the Python module against the core static library
target_link_libraries(fintechx_native PRIVATE fintechx_core OpenSSL::SSL OpenSSL::Crypto)

# Include directories for the binding module
target_include_directories(fintechx_native PRIVATE include)

# Installation (optional, but good for packaging)
# This tells CMake where to install the Python module relative to CMAKE_INSTALL_PREFIX
# The exact path might need adjustment based on the Python environment/packaging tool
install(TARGETS fintechx_native
        LIBRARY DESTINATION fintechx_desktop/infrastructure
)

# Remove the placeholder file if it exists
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src/placeholder.cpp")
    file(REMOVE "${CMAKE_CURRENT_SOURCE_DIR}/src/placeholder.cpp")
endif()


