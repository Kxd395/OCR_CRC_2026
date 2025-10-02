#!/usr/bin/env python3
"""
Create a diagnostic grid overlay to help identify exact checkbox positions.
Shows a measurement grid with coordinates to verify alignment.
"""
import cv2
import numpy as np
import argparse
from pathlib import Path

def create_diagnostic_overlay(img_path, output_path):
    """Create diagnostic overlay with measurement grid and coordinates."""
    
    # Load image
    img = cv2.imread(str(img_path))
    if img is None:
        raise ValueError(f"Could not load image: {img_path}")
    
    height, width = img.shape[:2]
    overlay = img.copy()
    
    # Colors (BGR format)
    COLOR_MAJOR = (255, 0, 0)      # Blue - every 100px
    COLOR_MINOR = (100, 100, 100)  # Gray - every 50px
    COLOR_CHECKBOX = (0, 255, 0)   # Green - documented checkbox positions
    COLOR_TEXT = (255, 255, 0)     # Cyan - coordinate labels
    COLOR_EXPECTED_X = (0, 165, 255)  # Orange - expected X lines
    COLOR_EXPECTED_Y = (255, 0, 255)  # Magenta - expected Y lines
    
    # Draw minor grid (every 50px)
    for x in range(0, width, 50):
        cv2.line(overlay, (x, 0), (x, height), COLOR_MINOR, 1)
    for y in range(0, height, 50):
        cv2.line(overlay, (0, y), (width, y), COLOR_MINOR, 1)
    
    # Draw major grid (every 100px) with labels
    for x in range(0, width, 100):
        cv2.line(overlay, (x, 0), (x, height), COLOR_MAJOR, 2)
        # Add coordinate label at top
        cv2.putText(overlay, str(x), (x+5, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT, 2)
        # Add coordinate label at bottom
        cv2.putText(overlay, str(x), (x+5, height-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT, 2)
    
    for y in range(0, height, 100):
        cv2.line(overlay, (0, y), (width, y), COLOR_MAJOR, 2)
        # Add coordinate label at left
        cv2.putText(overlay, str(y), (5, y+20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT, 2)
        # Add coordinate label at right
        cv2.putText(overlay, str(y), (width-60, y+20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT, 2)
    
    # Draw EXPECTED checkbox X positions (vertical lines in orange)
    expected_x = [280, 690, 1100, 1505, 1915]
    for x in expected_x:
        cv2.line(overlay, (x, 0), (x, height), COLOR_EXPECTED_X, 3)
        # Label at multiple heights for visibility
        cv2.putText(overlay, f"X:{x}", (x+5, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_EXPECTED_X, 2)
        cv2.putText(overlay, f"X:{x}", (x+5, height//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_EXPECTED_X, 2)
    
    # Draw EXPECTED checkbox Y positions (horizontal lines in magenta)
    expected_y = [1290, 1585, 1875, 2150, 2440]
    row_labels = ["R1", "R2", "R3", "R4", "R5"]
    for y, label in zip(expected_y, row_labels):
        cv2.line(overlay, (0, y), (width, y), COLOR_EXPECTED_Y, 3)
        # Label at multiple positions for visibility
        cv2.putText(overlay, f"{label}:Y={y}", (50, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_EXPECTED_Y, 2)
        cv2.putText(overlay, f"{label}:Y={y}", (width-200, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_EXPECTED_Y, 2)
    
    # Draw EXPECTED checkbox boxes (120x110px) in green
    box_width = 120
    box_height = 110
    for row_idx, y in enumerate(expected_y):
        for col_idx, x in enumerate(expected_x):
            # Draw rectangle
            cv2.rectangle(overlay, (x, y), (x + box_width, y + box_height), 
                         COLOR_CHECKBOX, 2)
            # Label the box
            box_label = f"Q{row_idx+1}_{col_idx+1}"
            cv2.putText(overlay, box_label, (x+5, y+25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_CHECKBOX, 2)
    
    # Add legend
    legend_y = 80
    legend_x = 50
    cv2.putText(overlay, "LEGEND:", (legend_x, legend_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(overlay, f"Blue = Major grid (100px)", (legend_x, legend_y+30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_MAJOR, 2)
    cv2.putText(overlay, f"Gray = Minor grid (50px)", (legend_x, legend_y+55), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_MINOR, 2)
    cv2.putText(overlay, f"Orange = Expected X coords", (legend_x, legend_y+80), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_EXPECTED_X, 2)
    cv2.putText(overlay, f"Magenta = Expected Y coords", (legend_x, legend_y+105), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_EXPECTED_Y, 2)
    cv2.putText(overlay, f"Green = Expected checkboxes (120x110)", (legend_x, legend_y+130), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_CHECKBOX, 2)
    
    # Add image info
    info_text = f"Image: {width} x {height} px"
    cv2.putText(overlay, info_text, (50, height-50), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Save
    cv2.imwrite(str(output_path), overlay)
    print(f"✅ Created diagnostic grid overlay: {output_path}")
    print(f"   Image size: {width} x {height} px")
    print(f"   Expected checkbox X: {expected_x}")
    print(f"   Expected checkbox Y: {expected_y}")
    print(f"   Box dimensions: {box_width} x {box_height} px")
    
    return overlay

def main():
    parser = argparse.ArgumentParser(description="Create diagnostic measurement grid overlay")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output", help="Output image path (default: input_diagnostic.png)")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.parent / f"{input_path.stem}_diagnostic.png"
    
    create_diagnostic_overlay(input_path, output_path)

if __name__ == "__main__":
    main()
