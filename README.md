# 🛠️ My Skills

个人使用的 Skills 合集，用于扩展 Kimi 的能力，提升开发效率。

## 📦 已收录 Skills

| Skill                           | 描述                                                       | 路径              |
| ------------------------------- | ---------------------------------------------------------- | ----------------- |
| [svg-to-png](./svg-to-png/)     | 将 SVG 文件转换为 PNG 格式，支持自动尺寸检测和高清输出     | `svg-to-png/`     |
| [mt2zh](./mt2zh/)               | 使用 AI 翻译 PDF 文档，支持批量处理和双语/译文模式         | `mt2zh/`          |
| [cmake-version-gen](./cmake-version-gen/) | 为 CMake C++ 项目自动生成版本头文件和 version.txt          | `cmake-version-gen/` |

## 🚀 快速开始

### 安装 Kimi CLI

```bash
pip install kimi-cli
# 或使用 uv
uv tool install kimi-cli
```

### 使用 Skills

Kimi CLI 会自动检测并使用项目中的 skills。你也可以通过以下方式配置全局 skills 路径：

```bash
# 查看当前配置
kimi config get skills

# 设置全局 skills 目录（可选）
kimi config set skills ~/.config/agents/skills
```

## 📁 项目结构

```
my-skills/
├── README.md               # 本文件
├── svg-to-png/             # SVG 转 PNG 工具
│   ├── SKILL.md            # Skill 定义和使用文档
│   └── scripts/
│       └── svg2png.py      # 转换脚本
├── mt2zh/                  # PDF 翻译工具
│   ├── SKILL.md
│   └── scripts/
│       └── translate.py
└── cmake-version-gen/      # CMake 版本生成工具
    ├── SKILL.md
    └── GenerateVersion.cmake
└── ...                     # 更多 skills 即将到来
```

每个 skill 目录包含：

- `SKILL.md` - Skill 定义、描述和使用说明
- `scripts/` - 相关的脚本文件（如有需要）

## 🔧 Skills 详情

### svg-to-png

将 SVG 矢量图形转换为 PNG 位图，支持自动检测 SVG 原生尺寸、高清/Retina 缩放和自定义输出参数。

**快速使用：**

```bash
# 自动检测尺寸
uv run svg-to-png/scripts/svg2png.py input.svg

# 高清输出（2x）
uv run svg-to-png/scripts/svg2png.py input.svg --hd

# 指定尺寸
uv run svg-to-png/scripts/svg2png.py input.svg -w 512 -H 512
```

[查看完整文档 →](./svg-to-png/SKILL.md)

### mt2zh

使用 `pdf2zh`（v1.9.11，即原 pdf2zh-next）和 OpenAI 兼容 API 翻译 PDF 文档。支持单个文件翻译、批量目录翻译、双语/仅译文输出模式，以及多线程并发处理。

**环境变量：**

| 变量 | 说明 |
|------|------|
| `MT_API_KEY` | OpenAI API Key（必填） |
| `MT_BASE_URL` | OpenAI API 地址（必填） |
| `MT_MODEL` | 模型名称（可选，默认 `qwen-plus`） |

**快速使用：**

```bash
# 翻译单个 PDF（自动检测源语言，目标语言为中文，生成 -mono 和 -dual 两个文件）
uv run mt2zh/scripts/translate.py document.pdf

# 批量翻译目录下所有 PDF
uv run mt2zh/scripts/translate.py ./docs --dir

# 仅保留译文（删除双语文件）
uv run mt2zh/scripts/translate.py doc.pdf --mode mono

# 仅保留双语对照（删除纯译文文件）
uv run mt2zh/scripts/translate.py doc.pdf --mode dual

# 使用系统全部核心加速
uv run mt2zh/scripts/translate.py ./documents --dir --threads auto

# 指定源语言和目标语言
uv run mt2zh/scripts/translate.py doc.pdf --lang-in en --lang-out zh

# 指定输出目录
uv run mt2zh/scripts/translate.py doc.pdf --output ./output

# 覆盖模型（不修改环境变量）
uv run mt2zh/scripts/translate.py doc.pdf --model qwen-max
```

[查看完整文档 →](./mt2zh/SKILL.md)

### cmake-version-gen

为 CMake C++ 项目注入自动版本生成模块，从 `project(VERSION x.y.z)`、Git 仓库和构建时间中提取版本信息，生成 C++ 头文件和 `version.txt`。

**快速使用：**

在 Kimi CLI 中直接调用 skill：

```bash
# 自动检测并部署版本生成模块
kimi skill cmake-version-gen
```

部署后，根 `CMakeLists.txt` 中会自动包含类似配置：

```cmake
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(GenerateVersion)
generate_version_info(
    PREFIX "MY_PROJECT"
    OUTPUT_DIR "${CMAKE_BINARY_DIR}/generated"
    OUTPUT_HEADER "${CMAKE_BINARY_DIR}/generated/my_project_version.h"
    OUTPUT_TXT "${CMAKE_BINARY_DIR}/version.txt"
)
set(MY_PROJECT_GENERATED_DIR "${CMAKE_BINARY_DIR}/generated")
```

子模块通过 `target_include_directories(PRIVATE "${MY_PROJECT_GENERATED_DIR}")` 引入版本头文件即可使用。

[查看完整文档 →](./cmake-version-gen/SKILL.md)

---

## ➕ 添加新 Skill

要添加新的 skill，请遵循以下结构：

```
new-skill/
├── SKILL.md          # 必须：包含 name 和 description frontmatter
└── scripts/          # 可选：相关脚本文件
    └── tool.py
```

`SKILL.md` 模板：

```markdown
---
name: skill-name
description: 简短描述该 skill 的功能和用途
---

# Skill 名称

详细描述...

## 使用方法

...
```

添加后记得更新本 README 中的技能列表。

## 📜 License

MIT License - 自由使用和修改

---

_持续更新中..._ ✨
