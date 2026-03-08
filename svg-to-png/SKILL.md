---
name: svg-to-png
description: Convert SVG files to PNG format with automatic dimension detection and high-definition support. Use when converting SVG vector graphics to PNG raster images, creating icons from SVG files, or generating high-resolution outputs from SVG. Supports auto-detection of SVG native dimensions, HD/Retina scaling, and customizable output parameters.
---

# SVG to PNG Converter

Convert SVG files to PNG format using PyMuPDF (fitz) with automatic SVG dimension detection and high-definition rendering support.

## Prerequisites

Install dependencies using uv:

```bash
uv pip install pymupdf
```

## Features

- **Auto-detect SVG dimensions**: Automatically reads width/height/viewBox from SVG files
- **High-definition output**: Support for 2x/3x/4x scaling for Retina displays
- **Flexible sizing**: Override dimensions or use native SVG size
- **Aspect ratio preservation**: Maintains aspect ratio when only one dimension is specified

## Usage

### Command Line

```bash
# Auto-detect dimensions and use native SVG size
uv run scripts/svg2png.py input.svg

# Generate HD image (2x native resolution)
uv run scripts/svg2png.py input.svg --hd

# Custom HD scale (3x, 4x, etc.)
uv run scripts/svg2png.py input.svg --hd --hd-scale 3

# Specific output size
uv run scripts/svg2png.py input.svg -w 512

# Both dimensions (may distort aspect ratio)
uv run scripts/svg2png.py input.svg -w 512 -H 512

# Scale factor
uv run scripts/svg2png.py input.svg --scale 1.5

# Verbose output with dimension info
uv run scripts/svg2png.py input.svg -v
```

### Python API

```python
from scripts.svg2png import convert_svg_to_png

# Auto-detect native dimensions
convert_svg_to_png("input.svg")

# HD output (2x native resolution)
convert_svg_to_png("input.svg", hd=True)

# Custom HD scale (3x)
convert_svg_to_png("input.svg", hd=True, hd_scale=3)

# Specific size with HD
convert_svg_to_png("input.svg", width=256, hd=True)

# Get dimension info
from scripts.svg2png import parse_svg_dimensions
width, height = parse_svg_dimensions("input.svg")
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input` | required | Input SVG file path |
| `output` | `{input}.png` | Output PNG file path |
| `width` | auto | Output width in pixels (default: from SVG) |
| `height` | auto | Output height in pixels (default: from SVG) |
| `scale` | 1.0 | Scale factor applied to output |
| `hd` | False | Generate high-definition image (2x scale) |
| `hd_scale` | 2.0 | HD scale factor when hd=True |
| `dpi` | 150 | Rendering DPI |
| `verbose` | False | Print dimension information |

## Default Behavior

- **Without `-w`/`-H`**: Uses SVG native dimensions from width/height/viewBox
- **With `--hd`**: Generates 2x resolution image (e.g., 100x100 SVG → 200x200 PNG)
- **With `-w` only**: Calculates height to maintain aspect ratio
- **With `-H` only**: Calculates width to maintain aspect ratio
- **With both `-w -H`**: May distort aspect ratio to fit exact dimensions

## Examples

### Create icon set
```bash
# Native size (from SVG)
uv run scripts/svg2png.py icon.svg -o icon.png

# Standard icon sizes with HD
uv run scripts/svg2png.py icon.svg -w 16 --hd -o icon-16@2x.png
uv run scripts/svg2png.py icon.svg -w 32 --hd -o icon-32@2x.png
uv run scripts/svg2png.py icon.svg -w 128 --hd -o icon-128@2x.png
```

### Web assets
```bash
# Regular display
uv run scripts/svg2png.py logo.svg -w 200

# Retina display (2x)
uv run scripts/svg2png.py logo.svg -w 200 --hd -o logo@2x.png
```
