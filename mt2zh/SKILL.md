---
name: mt2zh
description: >
  PDF 翻译工具，基于 pdf2zh（v1.9.11，即原 pdf2zh-next）和 OpenAI 兼容 API（默认使用 qwen 模型）。
  在用户需要以下操作时使用此技能：
  (1) 翻译单个 PDF 文件；
  (2) 批量翻译目录下所有 PDF；
  (3) 按扩展名筛选并翻译文件；
  (4) 指定源语言/目标语言（不指定时自动翻译成中文）；
  (5) 选择双语显示（原文+译文）或仅译文模式；
  (6) 控制翻译线程数（默认/自定义/自动匹配 CPU 核数）。
  触发关键词：翻译 PDF、PDF 翻译、mt2zh、translate PDF、pdf2zh。
---

# mt2zh — PDF 翻译工具

使用 `scripts/translate.py` 完成所有翻译任务。通过 `uv run` 或 `python` 执行。

> 底层调用 `pdf2zh` CLI（包名 `pdf2zh`，v1.9.11）。`pdf2zh-next` 是该项目新版本的曾用名，最终发布时仍以 `pdf2zh` 为包名，两者为同一项目。

## 环境变量

| 变量 | 说明 |
|------|------|
| `MT_API_KEY` | OpenAI API Key（必填） |
| `MT_BASE_URL` | OpenAI API 地址（必填） |
| `MT_MODEL` | 模型名称（可选，默认 `qwen-plus`） |

脚本自动将 `MT_*` 变量映射为 `pdf2zh` 所需的 `OPENAI_*` 变量。

## 命令速查

```bash
SKILL_DIR="<skill_path>/scripts"   # 此技能的 scripts 目录

# 翻译单个文件（自动翻译成中文，生成 -mono 和 -dual 两个文件）
python "$SKILL_DIR/translate.py" document.pdf

# 翻译目录下所有 PDF
python "$SKILL_DIR/translate.py" ./docs --dir

# 按扩展名筛选（翻译目录下所有 .pdf 和 .PDF）
python "$SKILL_DIR/translate.py" ./docs --dir --ext ".pdf,.PDF"

# 指定源语言和目标语言
python "$SKILL_DIR/translate.py" doc.pdf --lang-in en --lang-out zh

# 仅保留译文（删除双语文件）
python "$SKILL_DIR/translate.py" doc.pdf --mode mono

# 仅保留双语对照（删除纯译文文件）
python "$SKILL_DIR/translate.py" doc.pdf --mode dual

# 线程控制
python "$SKILL_DIR/translate.py" doc.pdf --threads 4      # 指定 4 线程
python "$SKILL_DIR/translate.py" doc.pdf --threads auto   # 自动匹配 CPU 核数

# 指定输出目录
python "$SKILL_DIR/translate.py" doc.pdf --output ./output

# 覆盖模型（不修改环境变量）
python "$SKILL_DIR/translate.py" doc.pdf --model qwen-max
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `input` | — | PDF 文件路径，或目录路径（配合 `--dir`） |
| `--dir` | — | 将 input 视为目录，递归查找匹配文件 |
| `--ext` | `.pdf` | 目录模式下匹配的扩展名，逗号分隔 |
| `--lang-in` | 自动检测 | 源语言代码（如 `en`、`ja`） |
| `--lang-out` | `zh` | 目标语言代码 |
| `--mode` | `both` | 输出模式：`both`/`mono`/`dual` |
| `--threads` | pdf2zh 默认 | 线程数，支持整数或 `auto` |
| `--output` | 与输入同目录 | 输出目录 |
| `--model` | 读取 `MT_MODEL` | 覆盖当前使用的模型 |

## 输出文件

pdf2zh 始终生成两个文件：

- `{filename}-mono.pdf` — 纯译文
- `{filename}-dual.pdf` — 双语对照（原文 + 译文）

`--mode mono` 自动删除 dual 文件；`--mode dual` 自动删除 mono 文件；`--mode both`（默认）保留全部。

## 执行步骤

1. 读取 `scripts/translate.py` 的绝对路径（`Read` 工具查看本技能目录）
2. 确认环境变量 `MT_API_KEY`、`MT_BASE_URL` 已设置
3. 根据用户需求组合参数，用 `Bash` 工具执行
4. 翻译完成后，向用户报告输出文件路径
