if(NOT DEFINED KTOOLS_CMAKE_MINIMUM_VERSION OR KTOOLS_CMAKE_MINIMUM_VERSION STREQUAL "")
    set(KTOOLS_CMAKE_MINIMUM_VERSION "3.20")
endif()
cmake_minimum_required(VERSION ${KTOOLS_CMAKE_MINIMUM_VERSION})

project(ktrace_python_demo_core LANGUAGES NONE)

set(_ktrace_python_demo_core_kbuild_vars
    "${BUILD_TESTING}"
    "${CMAKE_FIND_PACKAGE_PREFER_CONFIG}"
    "${KTOOLS_DEMO_BUILD_SHARED}"
    "${KTOOLS_DEMO_BUILD_STATIC}"
    "${KTOOLS_RUNTIME_RPATH_DIRS}"
    "${KcliSDK_DIR}"
    "${KtraceSDK_DIR}"
)

set(_ktrace_python_demo_core_script_src "${CMAKE_CURRENT_SOURCE_DIR}/main.py")
set(_ktrace_python_demo_core_script_dst "${CMAKE_CURRENT_BINARY_DIR}/test")

configure_file("${_ktrace_python_demo_core_script_src}" "${_ktrace_python_demo_core_script_dst}" COPYONLY)

file(CHMOD "${_ktrace_python_demo_core_script_dst}"
    PERMISSIONS
        OWNER_READ OWNER_WRITE OWNER_EXECUTE
        GROUP_READ GROUP_EXECUTE
        WORLD_READ WORLD_EXECUTE
)

add_custom_target(ktrace_python_demo_core ALL
    DEPENDS "${_ktrace_python_demo_core_script_dst}"
)
