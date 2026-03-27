cmake_minimum_required(VERSION 3.20)

project(kcli_python LANGUAGES NONE)

set(_kcli_python_kbuild_vars
    "${BUILD_TESTING}"
    "${KCLI_BUILD_SHARED}"
    "${KCLI_BUILD_STATIC}"
)

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/KcliSDKConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/KcliSDKConfig.cmake"
    @ONLY
)

install(
    DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/kcli"
    DESTINATION "python"
    FILES_MATCHING
        PATTERN "*.py"
        PATTERN "__pycache__" EXCLUDE
)

install(
    FILES "${CMAKE_CURRENT_BINARY_DIR}/KcliSDKConfig.cmake"
    DESTINATION "lib/cmake/KcliSDK"
)

install(CODE "file(MAKE_DIRECTORY \"\${CMAKE_INSTALL_PREFIX}/include\")")
