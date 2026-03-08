# 🛠️ My Skills

个人使用的 Skills 合集，用于扩展 Kimi 的能力，提升开发效率。

## 📦 已收录 Skills

| Skill                       | 描述                                                   | 路径          |
| --------------------------- | ------------------------------------------------------ | ------------- |
| [svg-to-png](./svg-to-png/) | 将 SVG 文件转换为 PNG 格式，支持自动尺寸检测和高清输出 | `svg-to-png/` |

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
├── README.md           # 本文件
├── svg-to-png/         # SVG 转 PNG 工具
│   ├── SKILL.md        # Skill 定义和使用文档
│   └── scripts/
│       └── svg2png.py  # 转换脚本
└── ...                 # 更多 skills 即将到来
```

每个 skill 目录包含：

- `SKILL.md` - Skill 定义、描述和使用说明
- `scripts/` - 相关的脚本文件（如有需要）

## 🔧 Skills 详情

### svg-to-png

将 SVG 矢量图形转换为 PNG 位图，支持自动检测 SVG 原生尺寸、高清/Retina 缩放和自定义输出参数。

**主要功能：**

- 自动读取 SVG 的 width/height/viewBox 属性
- 支持 2x/3x/4x 高清缩放
- 保持宽高比或自定义尺寸
- 命令行和 Python API 两种使用方式

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
