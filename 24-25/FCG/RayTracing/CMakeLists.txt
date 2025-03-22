cmake_minimum_required(VERSION 3.27)
project(FSproject VERSION 0.1.0 LANGUAGES C CXX)

set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../bin)

set(CMAKE_PDB_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

include(FetchContent)
FetchContent_Declare(
  sfml
  GIT_REPOSITORY https://github.com/SFML/SFML.git
  GIT_TAG      3.0.0 
  GIT_SHALLOW ON EXCLUDE_FROM_ALL
  SYSTEM
)
FetchContent_MakeAvailable(sfml)

add_executable(FSproject ./src/main.cpp)
target_link_libraries(FSproject PRIVATE 
SFML::Graphics
SFML::Window
SFML::System)