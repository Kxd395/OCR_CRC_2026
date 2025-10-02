#!/usr/bin/env python3
"""
Add a measurement grid overlay to an image for visual inspection.

Usage:
    python scripts/add_grid_to_image.py <input_image> [output_image] [--grid-size PIXELS]
"""
import argparse
import cv2
import numpy as np
from pathlib import Path


def add_grid_overlay(image_path, output_path=None, grid_size=50, thick_grid=100):
    """
    Add a measurement grid overlay to an image.
    
    Args:
        image_path: Path to input image
        output_path: Path to save output (default: input_grid.png)
        grid_size: Size of small grid squares in pixels
        thick_grid: Size of thick grid lines in pixels
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"ERROR: Could not load image: {image_path}")
        return None
    
    h, w = img.shape[:2]
    print(f"Image size: {w}×{h} pixels")
    
    # Create overlay
    overlay = img.copy()
    
    # Draw thin grid lines
    thin_color = (200, 200, 200)  # Light gray
    thick_color = (100, 100, 255)  # Orange/red
    
    # Vertical lines
    for x in range(0, w, grid_size):
        if x % thick_grid == 0:
            # Thick line every thick_grid pixels
            cv2.line(overlay, (x, 0), (x, h), thick_color, 2)
            # Add coordinate label
            cv2.putText(overlay, str(x), (x+5, 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, thick_color, 1)
        else:
            # Thin line
            cv2.line(overlay, (x, 0), (x, h), thin_color, 1)
    
    # Horizontal lines
    for y in range(0, h, grid_size):
        if y % thick_grid == 0:
            # Thick line every thick_grid pixels
            cv2.line(overlay, (0, y), (w, y), thick_color, 2)
            # Add coordinate label
            cv2.putText(overlay, str(y), (5, y+15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, thick_color, 1)
        else:
            # Thin line
            cv2.line(overlay, (0, y), (w, y), thin_color, 1)
    
    # Blend with original
    result = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)
    
    # Add grid info text
    info_text = f"Grid: {grid_size}px (thin), {thick_grid}px (thick) | Image: {w}×{h}px"
    cv2.rectangle(result, (0, h-40), (w, h), (0, 0, 0), -1)
    cv2.putText(result, info_text, (10, h-15), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Determine output path
    if output_path is None:
        input_path = Path(image_path)
        output_path = input_path.parent / f"{input_path.stem}_grid{input_path.suffix}"
    
    # Save result
    cv2.imwrite(str(output_path), result)
    print(f"✓ Grid overlay saved: {output_path}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Add measurement grid overlay to an image',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default 50px grid with 100px thick lines
  python scripts/add_grid_to_image.py image.png
  
  # Custom grid size
  python scripts/add_grid_to_image.py image.png --grid-size 25 --thick-grid 200
  
  # Custom output path
  python scripts/add_grid_to_image.py image.png output_grid.png
        """
    )
    
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', nargs='?', help='Output image path (optional)')
    parser.add_argument('--grid-size', type=int, default=50,
                       help='Small grid size in pixels (default: 50)')
    parser.add_argument('--thick-grid', type=int, default=100,
                       help='Thick grid line spacing in pixels (default: 100)')
    
    args = parser.parse_args()
    
    output = add_grid_overlay(args.input, args.output, args.grid_size, args.thick_grid)
    
    if output:
        return 0
    else:
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
