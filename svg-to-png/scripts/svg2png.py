#!/usr/bin/env python3
"""SVG to PNG converter using PyMuPDF (fitz).

Supports automatic SVG dimension detection and high-resolution output.
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF not installed. Install with: uv pip install pymupdf")
    sys.exit(1)


def parse_svg_dimensions(svg_path: str) -> Tuple[float, float]:
    """Parse SVG file to extract width and height from width/height attributes or viewBox.
    
    Args:
        svg_path: Path to SVG file
        
    Returns:
        Tuple of (width, height) in pixels
    """
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Remove namespace for easier access
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        width = None
        height = None
        
        # Try to get width and height attributes
        width_attr = root.get('width')
        height_attr = root.get('height')
        viewbox = root.get('viewBox')
        
        # Parse width
        if width_attr:
            width = parse_length(width_attr)
        
        # Parse height
        if height_attr:
            height = parse_length(height_attr)
        
        # If width/height not available, use viewBox
        if (width is None or height is None) and viewbox:
            # viewBox format: "minX minY width height"
            parts = viewbox.replace(',', ' ').split()
            if len(parts) >= 4:
                if width is None:
                    width = float(parts[2])
                if height is None:
                    height = float(parts[3])
        
        # Default fallback
        if width is None:
            width = 1000.0
        if height is None:
            height = 1000.0
            
        return (width, height)
    except Exception as e:
        # Fallback: use fitz to get dimensions
        doc = fitz.open(svg_path)
        rect = doc[0].rect
        return (rect.width, rect.height)


def parse_length(value: str) -> float:
    """Parse length value with unit (px, pt, em, etc.) to pixels.
    
    Args:
        value: Length string like "100px", "50", "72pt"
        
    Returns:
        Length in pixels
    """
    value = value.strip()
    
    # Extract number and unit
    match = re.match(r'^([\d.]+)\s*(px|pt|pc|in|mm|cm|em|ex|%)?$', value, re.IGNORECASE)
    if not match:
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    num = float(match.group(1))
    unit = (match.group(2) or 'px').lower()
    
    # Conversion factors (assuming 96 DPI)
    conversions = {
        'px': 1.0,
        'pt': 96 / 72,      # 1pt = 1.333px
        'pc': 96 / 6,       # 1pc = 16px
        'in': 96.0,          # 1in = 96px
        'mm': 96 / 25.4,    # 1mm = 3.78px
        'cm': 96 / 2.54,    # 1cm = 37.8px
        'em': 16.0,          # 1em = 16px (default)
        'ex': 8.0,           # 1ex ≈ 8px
    }
    
    return num * conversions.get(unit, 1.0)


def convert_svg_to_png(
    input_path: str,
    output_path: str | None = None,
    width: int | None = None,
    height: int | None = None,
    scale: float = 1.0,
    hd: bool = False,
    hd_scale: float = 2.0,
    dpi: int = 150,
    verbose: bool = False,
) -> str:
    """Convert SVG file to PNG.
    
    Args:
        input_path: Path to input SVG file
        output_path: Path to output PNG file (default: same name with .png)
        width: Output width in pixels (default: auto from SVG)
        height: Output height in pixels (default: auto from SVG)
        scale: Scale factor applied to output dimensions (default: 1.0)
        hd: Generate high-definition image (2x scale) (default: False)
        hd_scale: HD scale factor when hd=True (default: 2.0)
        dpi: DPI for rendering (default: 150)
        verbose: Print detailed information (default: False)
    
    Returns:
        Path to the output PNG file
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if output_path is None:
        output_path = input_file.with_suffix('.png')
    
    # Get SVG native dimensions
    native_width, native_height = parse_svg_dimensions(str(input_path))
    
    if verbose:
        print(f"SVG native dimensions: {native_width:.1f} x {native_height:.1f}")
    
    # Determine output dimensions
    if width is None and height is None:
        # Use native dimensions
        out_width = native_width
        out_height = native_height
    elif width is not None and height is not None:
        # Both specified
        out_width = width
        out_height = height
    elif width is not None:
        # Only width specified, calculate height
        out_width = width
        ratio = native_height / native_width
        out_height = out_width * ratio
    else:
        # Only height specified, calculate width
        out_height = height
        ratio = native_width / native_height
        out_width = out_height * ratio
    
    # Apply HD scaling
    if hd:
        scale = hd_scale
        if verbose:
            print(f"HD mode enabled: {hd_scale}x scale")
    
    # Apply user scale
    out_width *= scale
    out_height *= scale
    
    out_width = int(out_width)
    out_height = int(out_height)
    
    if verbose:
        print(f"Output dimensions: {out_width} x {out_height} (scale: {scale})")
    
    # Open SVG and render
    doc = fitz.open(str(input_path))
    page = doc[0]
    
    # Calculate scale factors
    scale_x = out_width / page.rect.width
    scale_y = out_height / page.rect.height
    
    mat = fitz.Matrix(scale_x, scale_y)
    
    # Render to pixmap
    pix = page.get_pixmap(matrix=mat)
    
    # Save
    pix.save(str(output_path))
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert SVG to PNG with automatic dimension detection and HD support"
    )
    parser.add_argument("input", help="Input SVG file path")
    parser.add_argument("-o", "--output", help="Output PNG file path (default: same name with .png)")
    parser.add_argument("-w", "--width", type=int, help="Output width in pixels (default: auto from SVG)")
    parser.add_argument("-H", "--height", type=int, help="Output height in pixels (default: auto from SVG)")
    parser.add_argument("-s", "--scale", type=float, default=1.0, help="Scale factor (default: 1.0)")
    parser.add_argument("--hd", action="store_true", help="Generate high-definition image (2x scale)")
    parser.add_argument("--hd-scale", type=float, default=2.0, help="HD scale factor (default: 2.0)")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for rendering (default: 150)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print detailed information")
    
    args = parser.parse_args()
    
    try:
        output = convert_svg_to_png(
            input_path=args.input,
            output_path=args.output,
            width=args.width,
            height=args.height,
            scale=args.scale,
            hd=args.hd,
            hd_scale=args.hd_scale,
            dpi=args.dpi,
            verbose=args.verbose,
        )
        print(f"Converted: {output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
