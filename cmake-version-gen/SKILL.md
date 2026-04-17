---
name: cmake-version-gen
description: Use when user wants to add or update automatic version generation in a CMake-based C++ project. Triggers include: 版本生成、GenerateVersion、CMake 版本、自动版本号、git version、build version、生成版本头文件。
---

# CMake C++ 项目自动版本生成

## 概述

为 CMake C++ 项目注入通用版本生成模块，自动从 `project(VERSION x.y.z)`、Git 仓库和构建时间中提取版本信息，生成 C++ 头文件和 `version.txt`。

> **模板位置**: `<SKILL_DIR>/GenerateVersion.cmake`
> **最低 CMake 版本**: 3.17（`add_version_target` 使用了 `CMAKE_CURRENT_FUNCTION_LIST_FILE`）

## 执行步骤

### 1. 确认项目类型

检查项目根目录是否存在 `CMakeLists.txt`。若不存在，告知用户此 skill 仅适用于 CMake 项目。

### 2. 确定项目前缀 (PREFIX)

PREFIX 是所有生成宏的命名空间前缀，用于防止多库共存时宏名冲突。必须是合法的 C 宏前缀（大写字母、数字、下划线）。

**手动指定（优先）**：直接询问用户希望使用什么前缀。用户可以用比项目名更短的别名，只要在项目中唯一即可。
- 示例：`project(SkylineEngineering)` 用户可以指定 PREFIX 为 `SKYLINE`、`SKYLINE_ENG`、`SKYLINEENGINEERING` 等任意合法值。

**自动推断（用户未指定时）**：将 `project()` 名称全部转大写，非字母数字字符替换为下划线。
- `SkylineEngineering` → `SKYLINEENGINEERING`
- `my-app` → `MY_APP`

### 3. 部署通用模块

- 确保项目根目录存在 `cmake/` 文件夹。
- 将 `<SKILL_DIR>/GenerateVersion.cmake` 复制到 `{项目根目录}/cmake/GenerateVersion.cmake`。

### 4. 修改根 `CMakeLists.txt`

在根 `CMakeLists.txt` 中完成以下插入（若已存在则跳过）：

1. **添加模块搜索路径**（通常放在 `project()` 之后）：
   ```cmake
   list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
   ```

2. **调用版本生成函数**（紧跟在 `project()` 或模块路径声明之后）：
   ```cmake
   include(GenerateVersion)
   generate_version_info(
       PREFIX "<PREFIX>"
       OUTPUT_DIR "${CMAKE_BINARY_DIR}/generated"
       OUTPUT_HEADER "${CMAKE_BINARY_DIR}/generated/<prefix_lower>_version.h"
       OUTPUT_TXT "${CMAKE_BINARY_DIR}/version.txt"
   )

   # 版本头文件目录（供所有子项目使用）
   set(<PREFIX>_GENERATED_DIR "${CMAKE_BINARY_DIR}/generated")
   ```

3. **确保 `project()` 带有版本号**：
   如果当前 `project()` 没有 `VERSION` 参数，应建议用户添加，例如：
   ```cmake
   project(MyProject VERSION 0.1.0 LANGUAGES CXX)
   ```

### 5. 修改子模块 `CMakeLists.txt`

对于需要引用版本头文件的 target（通常是库或可执行文件），在 `target_include_directories` 的 `PRIVATE` 部分添加：
```cmake
target_include_directories(
    <target_name>
    PRIVATE
        "${<PREFIX>_GENERATED_DIR}"
)
```

### 6. 拷贝 `version.txt` 到输出目录（可选但推荐）

若项目生成可执行文件或 DLL，为其添加 POST_BUILD 命令，将 `version.txt` 复制到目标输出目录：
```cmake
add_custom_command(
    TARGET <target_name> POST_BUILD
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different
        "${CMAKE_BINARY_DIR}/version.txt"
        "$<TARGET_FILE_DIR:<target_name>>/version.txt"
    VERBATIM
)
```

### 7. 验证

运行一次 CMake 配置，检查输出中是否出现类似：
```
-- <PREFIX> Version: 0.1.0-abc1234 (main)
```
并确认生成的头文件和 `version.txt` 内容正确。

### 8. 文档记录

在 `{项目根目录}/docs/design_summary.md` 中追加版本生成设计记录。

## 生成的宏清单

以 PREFIX `SKYLINE` 为例，生成的头文件包含：

| 宏 | 示例值 |
|---|---|
| `SKYLINE_VERSION` | `"0.1.0"` |
| `SKYLINE_VERSION_MAJOR` | `0` |
| `SKYLINE_VERSION_MINOR` | `1` |
| `SKYLINE_VERSION_PATCH` | `0` |
| `SKYLINE_GIT_COMMIT` | `"e54c284"` |
| `SKYLINE_GIT_BRANCH` | `"main"` |
| `SKYLINE_GIT_TAG` | `"v0.1.0"` |
| `SKYLINE_BUILD_TIMESTAMP` | `"2026-04-17T10:30:00"` |
| `SKYLINE_BUILD_DATE` | `"2026-04-17"` |
| `SKYLINE_VERSION_STRING` | 完整字符串宏 |
| `SKYLINE_VERSION_RC` | Windows 四段式版本号 |

## 注意事项

- 生成的头文件名默认为 `<prefix_lower>_version.h`（如 `skyline_version.h`）。
- 版本号优先从 `CMAKE_PROJECT_VERSION` 读取，因此根 `CMakeLists.txt` 中的 `project()` 必须带 `VERSION`。
- 在非 Git 仓库中运行时，Git 相关字段会回退为 `"unknown"`。
- 不要修改 `cmake/GenerateVersion.cmake` 中的通用逻辑；如需调整，应通过函数参数控制。

## 可选：每次构建时更新 Git 信息（`add_version_target`）

`generate_version_info` 在 CMake **configure 阶段**运行一次，Git commit 不会随每次构建自动刷新。若需要在每次 `cmake --build` 时更新 Git commit/branch，可使用 `add_version_target`：

```cmake
include(GenerateVersion)

# 先调用一次 generate_version_info 确保首次 configure 生成文件
generate_version_info(PREFIX "<PREFIX>" ...)

# 注册 build-time 更新目标（ALL 表示每次构建都执行）
add_version_target(version_update
    PREFIX "<PREFIX>"
    OUTPUT_DIR "${CMAKE_BINARY_DIR}/generated"
)

# 让需要版本头文件的 target 依赖此更新目标
add_dependencies(<target_name> version_update)
```

**注意**：
- 版本号（MAJOR/MINOR/PATCH）在 configure 阶段固化，build 时不会因修改 `project()` 而变化；需要版本号变更时重新 configure。
- Git commit/branch/tag 每次 build 都会重新读取。
- 需要 CMake ≥ 3.17。
