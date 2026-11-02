cmake_minimum_required(VERSION 3.20)
project(TheUncounted VERSION 1.0.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Place game.exe directly in the project root directory
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}")

# Configure raylib as a static foundation library
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(BUILD_GAMES OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
add_subdirectory(third_party/raylib)

add_executable(game
    src/main.cpp
    src/core/Logger.cpp
    src/content/ContentRegistry.cpp
    src/resource/ResourceManager.cpp
    src/gameplay/GameEngine.cpp
    src/gameplay/GameUI.cpp
    src/gameplay/SelfTest.cpp
    src/gameplay/BalanceSim.cpp
    src/renderer/WorldRenderer.cpp
)

target_include_directories(game PRIVATE
    "${CMAKE_SOURCE_DIR}/src"
    "${CMAKE_SOURCE_DIR}/third_party"
    "${CMAKE_SOURCE_DIR}/third_party/raylib/src"
)

target_link_libraries(game PRIVATE raylib)

if(WIN32)
    target_link_libraries(game PRIVATE winmm gdi32 opengl32)
endif()

# MinGW: link the C/C++ runtimes statically so game.exe runs without the toolchain on PATH.
if(MINGW)
    target_link_options(game PRIVATE -static -static-libgcc -static-libstdc++)
endif()
