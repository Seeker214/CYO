cmake_minimum_required(VERSION 3.15)
project(chaos_crypto_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find pybind11 (installed via pip)
find_package(pybind11 REQUIRED)

pybind11_add_module(chaos_crypto_cpp
    bindings.cpp
    chaos_sequence.cpp
    encryption.cpp
    decryption.cpp
    chaos_analysis.cpp
)

target_include_directories(chaos_crypto_cpp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Optimization flags
if(MSVC)
    target_compile_options(chaos_crypto_cpp PRIVATE /O2 /GL)
else()
    target_compile_options(chaos_crypto_cpp PRIVATE -O3 -march=native)
endif()

# Install to the cyo package directory
install(TARGETS chaos_crypto_cpp
    LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/cyo
)
