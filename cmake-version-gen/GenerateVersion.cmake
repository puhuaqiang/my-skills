# GenerateVersion.cmake - 通用自动生成版本信息模块
#
# 最低要求: CMake 3.17（使用了 CMAKE_CURRENT_FUNCTION_LIST_FILE）
#
# 功能：
#   - 获取 Git commit hash (short)
#   - 获取 Git 分支名
#   - 获取 Git 标签（describe --tags --always）
#   - 生成构建时间戳
#   - 生成版本头文件和版本文本文件
#
# 用法：
#   generate_version_info(
#       PREFIX "MYPROJECT"
#       [OUTPUT_DIR "${CMAKE_BINARY_DIR}/generated"]
#       [OUTPUT_HEADER "${CMAKE_BINARY_DIR}/generated/myproject_version.h"]
#       [OUTPUT_TXT "${CMAKE_BINARY_DIR}/version.txt"]
#       [VERSION "1.2.3"]         # 可选，优先级高于 CMAKE_PROJECT_VERSION
#       [VERSION_MAJOR "1"]       # 可选，优先级高于 CMAKE_PROJECT_VERSION_MAJOR
#       [VERSION_MINOR "2"]       # 可选，优先级高于 CMAKE_PROJECT_VERSION_MINOR
#       [VERSION_PATCH "3"]       # 可选，优先级高于 CMAKE_PROJECT_VERSION_PATCH
#   )
#
# 生成的文件：
#   - ${OUTPUT_HEADER} : C++ 头文件，包含版本宏
#   - ${OUTPUT_TXT}    : 文本版本文件

function(generate_version_info)
    set(options "")
    set(oneValueArgs PREFIX OUTPUT_DIR OUTPUT_HEADER OUTPUT_TXT VERSION VERSION_MAJOR VERSION_MINOR VERSION_PATCH)
    set(multiValueArgs "")
    cmake_parse_arguments(GENVER "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    # 默认值
    if(NOT GENVER_PREFIX)
        set(GENVER_PREFIX "PROJECT")
    endif()
    if(NOT GENVER_OUTPUT_DIR)
        set(GENVER_OUTPUT_DIR "${CMAKE_BINARY_DIR}/generated")
    endif()

    string(TOLOWER "${GENVER_PREFIX}" GENVER_PREFIX_LOWER)
    if(NOT GENVER_OUTPUT_HEADER)
        set(GENVER_OUTPUT_HEADER "${GENVER_OUTPUT_DIR}/${GENVER_PREFIX_LOWER}_version.h")
    endif()
    if(NOT GENVER_OUTPUT_TXT)
        set(GENVER_OUTPUT_TXT "${CMAKE_BINARY_DIR}/version.txt")
    endif()

    # 创建输出目录
    file(MAKE_DIRECTORY "${GENVER_OUTPUT_DIR}")

    # 获取 Git 信息
    find_package(Git QUIET)
    if(GIT_FOUND)
        execute_process(
            COMMAND "${GIT_EXECUTABLE}" rev-parse --short HEAD
            WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
            OUTPUT_VARIABLE GENVER_GIT_COMMIT
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        execute_process(
            COMMAND "${GIT_EXECUTABLE}" rev-parse --abbrev-ref HEAD
            WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
            OUTPUT_VARIABLE GENVER_GIT_BRANCH
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
        execute_process(
            COMMAND "${GIT_EXECUTABLE}" describe --tags --always
            WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
            OUTPUT_VARIABLE GENVER_GIT_TAG
            OUTPUT_STRIP_TRAILING_WHITESPACE
            ERROR_QUIET
        )
    endif()

    # 各字段独立 fallback，防止部分命令失败时留空
    if(NOT GENVER_GIT_COMMIT)
        set(GENVER_GIT_COMMIT "unknown")
    endif()
    if(NOT GENVER_GIT_BRANCH)
        set(GENVER_GIT_BRANCH "unknown")
    endif()
    if(NOT GENVER_GIT_TAG)
        set(GENVER_GIT_TAG "unknown")
    endif()

    # 生成构建时间戳 (ISO 8601 格式)
    string(TIMESTAMP GENVER_BUILD_TIMESTAMP "%Y-%m-%dT%H:%M:%S")
    string(TIMESTAMP GENVER_BUILD_DATE "%Y-%m-%d")
    set(GENVER_CONFIGURE_TIME "${GENVER_BUILD_TIMESTAMP}")

    # 项目版本：优先使用传入参数（供 build-time 脚本模式使用），其次读取 CMAKE_PROJECT_VERSION
    if(NOT GENVER_VERSION)
        if(CMAKE_PROJECT_VERSION)
            set(GENVER_VERSION "${CMAKE_PROJECT_VERSION}")
        else()
            set(GENVER_VERSION "0.1.0")
        endif()
    endif()

    if(NOT GENVER_VERSION_MAJOR)
        if(CMAKE_PROJECT_VERSION_MAJOR)
            set(GENVER_VERSION_MAJOR "${CMAKE_PROJECT_VERSION_MAJOR}")
        else()
            set(GENVER_VERSION_MAJOR 0)
        endif()
    endif()

    if(NOT GENVER_VERSION_MINOR)
        if(CMAKE_PROJECT_VERSION_MINOR)
            set(GENVER_VERSION_MINOR "${CMAKE_PROJECT_VERSION_MINOR}")
        else()
            set(GENVER_VERSION_MINOR 1)
        endif()
    endif()

    if(NOT GENVER_VERSION_PATCH)
        if(CMAKE_PROJECT_VERSION_PATCH)
            set(GENVER_VERSION_PATCH "${CMAKE_PROJECT_VERSION_PATCH}")
        else()
            set(GENVER_VERSION_PATCH 0)
        endif()
    endif()

    # 生成版本头文件内容
    set(VERSION_HEADER_CONTENT [=[#pragma once
/* 自动生成的版本信息文件 - 请勿手动修改 */
/* 生成时间: @GENVER_CONFIGURE_TIME@ */

#define @GENVER_PREFIX@_VERSION "@GENVER_VERSION@"
#define @GENVER_PREFIX@_VERSION_MAJOR @GENVER_VERSION_MAJOR@
#define @GENVER_PREFIX@_VERSION_MINOR @GENVER_VERSION_MINOR@
#define @GENVER_PREFIX@_VERSION_PATCH @GENVER_VERSION_PATCH@

#define @GENVER_PREFIX@_GIT_COMMIT "@GENVER_GIT_COMMIT@"
#define @GENVER_PREFIX@_GIT_BRANCH "@GENVER_GIT_BRANCH@"
#define @GENVER_PREFIX@_GIT_TAG "@GENVER_GIT_TAG@"

#define @GENVER_PREFIX@_BUILD_TIMESTAMP "@GENVER_BUILD_TIMESTAMP@"
#define @GENVER_PREFIX@_BUILD_DATE "@GENVER_BUILD_DATE@"

// 完整版本字符串
#define @GENVER_PREFIX@_VERSION_STRING @GENVER_PREFIX@_VERSION "-" @GENVER_PREFIX@_GIT_COMMIT " (" @GENVER_PREFIX@_GIT_BRANCH ")"

// Windows 资源文件版本号 (四段式)
#define @GENVER_PREFIX@_VERSION_RC @GENVER_VERSION_MAJOR@,@GENVER_VERSION_MINOR@,@GENVER_VERSION_PATCH@,0
]=])

    string(CONFIGURE "${VERSION_HEADER_CONTENT}" GENERATED_HEADER @ONLY)
    file(WRITE "${GENVER_OUTPUT_HEADER}" "${GENERATED_HEADER}")

    # 生成版本文本文件
    set(VERSION_TXT_CONTENT [=[Version: @GENVER_VERSION@
Git Commit: @GENVER_GIT_COMMIT@
Git Branch: @GENVER_GIT_BRANCH@
Git Tag: @GENVER_GIT_TAG@
Build Time: @GENVER_BUILD_TIMESTAMP@
]=])

    string(CONFIGURE "${VERSION_TXT_CONTENT}" GENERATED_TXT @ONLY)
    file(WRITE "${GENVER_OUTPUT_TXT}" "${GENERATED_TXT}")

    # 设置输出变量供父作用域使用
    set(${GENVER_PREFIX}_VERSION        "${GENVER_VERSION}"         PARENT_SCOPE)
    set(${GENVER_PREFIX}_GIT_COMMIT     "${GENVER_GIT_COMMIT}"      PARENT_SCOPE)
    set(${GENVER_PREFIX}_GIT_BRANCH     "${GENVER_GIT_BRANCH}"      PARENT_SCOPE)
    set(${GENVER_PREFIX}_GIT_TAG        "${GENVER_GIT_TAG}"         PARENT_SCOPE)
    set(${GENVER_PREFIX}_BUILD_TIMESTAMP "${GENVER_BUILD_TIMESTAMP}" PARENT_SCOPE)

    message(STATUS "${GENVER_PREFIX} Version: ${GENVER_VERSION}-${GENVER_GIT_COMMIT} (${GENVER_GIT_BRANCH})")
endfunction()

# 添加版本信息目标 - 每次构建时重新生成（需要 CMake >= 3.17）
#
# 用法：
#   add_version_target(<target_name>
#       [PREFIX "MYPROJECT"]
#       [OUTPUT_DIR "${CMAKE_BINARY_DIR}/generated"]
#   )
#
# 生成的目标会在每次 cmake --build 时运行，刷新 Git commit/branch 信息。
# 版本号在 configure 阶段固化并通过 -D 传入，不依赖脚本模式下的 CMAKE_PROJECT_VERSION。
function(add_version_target target_name)
    set(options "")
    set(oneValueArgs PREFIX OUTPUT_DIR)
    set(multiValueArgs "")
    cmake_parse_arguments(GENVER "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

    if(NOT GENVER_PREFIX)
        set(GENVER_PREFIX "PROJECT")
    endif()
    if(NOT GENVER_OUTPUT_DIR)
        set(GENVER_OUTPUT_DIR "${CMAKE_BINARY_DIR}/generated")
    endif()

    string(TOLOWER "${GENVER_PREFIX}" GENVER_PREFIX_LOWER)
    set(HEADER_FILE "${GENVER_OUTPUT_DIR}/${GENVER_PREFIX_LOWER}_version.h")
    set(TXT_FILE "${CMAKE_BINARY_DIR}/version.txt")

    # 使用 ALL 确保每次 build 都执行；BYPRODUCTS 声明生成文件供依赖追踪
    # 版本号在 configure 时固化通过 -D 传入，解决 script 模式无 CMAKE_PROJECT_VERSION 问题
    add_custom_target(${target_name} ALL
        COMMAND "${CMAKE_COMMAND}"
            "-D" "GENVER_PREFIX=${GENVER_PREFIX}"
            "-D" "GENVER_VERSION=${CMAKE_PROJECT_VERSION}"
            "-D" "GENVER_VERSION_MAJOR=${CMAKE_PROJECT_VERSION_MAJOR}"
            "-D" "GENVER_VERSION_MINOR=${CMAKE_PROJECT_VERSION_MINOR}"
            "-D" "GENVER_VERSION_PATCH=${CMAKE_PROJECT_VERSION_PATCH}"
            "-D" "GENVER_OUTPUT_DIR=${GENVER_OUTPUT_DIR}"
            "-D" "GENVER_OUTPUT_HEADER=${HEADER_FILE}"
            "-D" "GENVER_OUTPUT_TXT=${TXT_FILE}"
            "-P" "${CMAKE_CURRENT_FUNCTION_LIST_FILE}"
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        COMMENT "Generating version information"
        BYPRODUCTS "${HEADER_FILE}" "${TXT_FILE}"
        VERBATIM
    )
endfunction()

# 主入口 - 脚本模式运行（由 add_version_target 的 cmake -P 调用）
if(CMAKE_SCRIPT_MODE_FILE)
    generate_version_info(
        PREFIX        "${GENVER_PREFIX}"
        OUTPUT_DIR    "${GENVER_OUTPUT_DIR}"
        OUTPUT_HEADER "${GENVER_OUTPUT_HEADER}"
        OUTPUT_TXT    "${GENVER_OUTPUT_TXT}"
        VERSION       "${GENVER_VERSION}"
        VERSION_MAJOR "${GENVER_VERSION_MAJOR}"
        VERSION_MINOR "${GENVER_VERSION_MINOR}"
        VERSION_PATCH "${GENVER_VERSION_PATCH}"
    )
endif()
