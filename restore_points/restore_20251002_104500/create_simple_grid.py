#!/usr/bin/env python3
"""
Create a simple grid overlay on the image with lines every 1000 pixels.
Red for vertical lines, green for horizontal lines.
"""

import cv2
import numpy as np
from pathlib import Path


def create_grid_overlay(image_path: Path, output_path: Path, grid_spacing_50: int = 50, grid_spacing_100: int = 100):
    """
    Create grid overlay with lines every 50px and every 100px.
    
    Args:
        image_path: Path to input image
        output_path: Path to save output
        grid_spacing_50: Spacing for thin lines (default: 50)
        grid_spacing_100: Spacing for thick red lines (default: 100)
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    
    height, width = img.shape[:2]
    print(f"Image dimensions: {width}x{height}px")
    
    # Create overlay
    overlay = img.copy()
    
    # Draw vertical lines every 50px (thin green) and every 100px (thick red)
    print(f"\nDrawing vertical lines:")
    for x in range(0, width + 1, grid_spacing_50):
        if x % grid_spacing_100 == 0:
            # Every 100px - thick RED line
            cv2.line(overlay, (x, 0), (x, height), (0, 0, 255), 2)
            print(f"  RED line at x={x}")
            # Add label at top
            label = f"{x}"
            cv2.putText(
                overlay,
                label,
                (x + 5, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )
        else:
            # Every 50px - thin GREEN line
            cv2.line(overlay, (x, 0), (x, height), (0, 255, 0), 1)
    
    # Draw horizontal lines every 50px (thin green) and every 100px (thick red)
    print(f"\nDrawing horizontal lines:")
    for y in range(0, height + 1, grid_spacing_50):
        if y % grid_spacing_100 == 0:
            # Every 100px - thick RED line
            cv2.line(overlay, (0, y), (width, y), (0, 0, 255), 2)
            print(f"  RED line at y={y}")
            # Add label at left
            label = f"{y}"
            cv2.putText(
                overlay,
                label,
                (10, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )
        else:
            # Every 50px - thin GREEN line
            cv2.line(overlay, (0, y), (width, y), (0, 255, 0), 1)
    
    # Add info box
    info_box_height = 120
    cv2.rectangle(overlay, (10, height - info_box_height - 10), 
                  (400, height - 10), (0, 0, 0), -1)
    cv2.rectangle(overlay, (10, height - info_box_height - 10), 
                  (400, height - 10), (255, 255, 255), 2)
    
    y_offset = height - info_box_height + 5
    cv2.putText(overlay, f"Image: {width}x{height}px", 
                (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    y_offset += 30
    cv2.putText(overlay, f"Grid: Every {grid_spacing_50}px (green), Every {grid_spacing_100}px (red)", 
                (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    y_offset += 30
    cv2.putText(overlay, "RED (thick) = Every 100px", 
                (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    y_offset += 25
    cv2.putText(overlay, "GREEN (thin) = Every 50px", 
                (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Save
    cv2.imwrite(str(output_path), overlay)
    print(f"\n✅ Saved grid overlay to: {output_path}")
    
    return width, height


if __name__ == "__main__":
    import sys
    
    # Paths
    project_root = Path(__file__).parent.parent
    run_dir = project_root / "artifacts/run_20251001_185300"
    
    image_path = run_dir / "02_step2_alignment_and_crop/aligned_cropped/page_0001_aligned_cropped.png"
    output_path = run_dir / "grid_overlay_1000px.png"
    
    # Check if image exists
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print("Creating grid overlay with 50px and 100px spacing...")
    print(f"Input: {image_path}")
    print(f"Output: {output_path}")
    
    # Create grid
    width, height = create_grid_overlay(image_path, output_path, grid_spacing_50=50, grid_spacing_100=100)
    
    print(f"\n{'='*60}")
    print("GRID COORDINATES")
    print(f"{'='*60}")
    print("\nGreen lines (thin) every 50px: 0, 50, 100, 150, 200, ...")
    print("Red lines (thick) every 100px: 0, 100, 200, 300, 400, ...")
    print(f"\nTotal image: {width}x{height}px")
    print(f"{'='*60}")
    
    print(f"\nOpen the image to find checkbox locations:")
    print(f"  {output_path}")
