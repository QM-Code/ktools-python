cmake_minimum_required(VERSION 3.20)

project(ktrace_python LANGUAGES NONE)

set(_ktrace_python_kbuild_vars
    "${BUILD_TESTING}"
    "${CMAKE_FIND_PACKAGE_PREFER_CONFIG}"
    "${KTOOLS_RUNTIME_RPATH_DIRS}"
    "${KTRACE_BUILD_SHARED}"
    "${KTRACE_BUILD_STATIC}"
    "${KcliSDK_DIR}"
)

configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/KtraceSDKConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/KtraceSDKConfig.cmake"
    @ONLY
)

install(
    DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/ktrace"
    DESTINATION "python"
    FILES_MATCHING
        PATTERN "*.py"
        PATTERN "__pycache__" EXCLUDE
)

install(
    FILES "${CMAKE_CURRENT_BINARY_DIR}/KtraceSDKConfig.cmake"
    DESTINATION "lib/cmake/KtraceSDK"
)

install(CODE "file(MAKE_DIRECTORY \"\${CMAKE_INSTALL_PREFIX}/include\")")
