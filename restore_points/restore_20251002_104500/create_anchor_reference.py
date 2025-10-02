#!/usr/bin/env python3
"""
Create an annotated anchor position reference image with grid and coordinate markers.
Shows expected anchor positions with clear labels for easy identification.
"""
import cv2
import numpy as np
from pathlib import Path
import json


def create_anchor_reference_image(image_path, template_path, output_path=None):
    """Create reference image with grid and labeled anchor positions."""
    
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"ERROR: Could not load image: {image_path}")
        return None
    
    h, w = img.shape[:2]
    print(f"Image size: {w}×{h} pixels")
    
    # Load template to get expected anchor positions
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # Get page size from template (reference dimensions)
    ref_w = template['page_size']['width_px']
    ref_h = template['page_size']['height_px']
    print(f"Template reference: {ref_w}×{ref_h} pixels")
    
    # Calculate scaling factor
    scale_w = w / ref_w
    scale_h = h / ref_h
    print(f"Scale factors: width={scale_w:.3f}, height={scale_h:.3f}")
    
    # Get anchors
    anchors_norm = template['anchors_norm']
    anchor_labels = ['TL (Top-Left)', 'TR (Top-Right)', 'BR (Bottom-Right)', 'BL (Bottom-Left)']
    
    # Create output image with grid
    result = img.copy()
    
    # Draw measurement grid
    grid_size = 50
    thick_grid = 100
    
    # Thin grid lines (light gray)
    for x in range(0, w, grid_size):
        color = (100, 100, 255) if x % thick_grid == 0 else (200, 200, 200)
        thickness = 2 if x % thick_grid == 0 else 1
        cv2.line(result, (x, 0), (x, h), color, thickness)
        
        # Add X coordinate labels on thick lines
        if x % thick_grid == 0:
            cv2.putText(result, f"X:{x}", (x+5, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
    
    for y in range(0, h, grid_size):
        color = (100, 100, 255) if y % thick_grid == 0 else (200, 200, 200)
        thickness = 2 if y % thick_grid == 0 else 1
        cv2.line(result, (0, y), (w, y), color, thickness)
        
        # Add Y coordinate labels on thick lines
        if y % thick_grid == 0:
            cv2.putText(result, f"Y:{y}", (10, y+20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
    
    # Draw expected anchor positions
    for i, (anchor, label) in enumerate(zip(anchors_norm, anchor_labels)):
        # Convert normalized coordinates to pixel coordinates
        # Use reference dimensions from template, then scale to image
        x_ref = anchor['x'] * ref_w
        y_ref = anchor['y'] * ref_h
        x = int(x_ref * scale_w)
        y = int(y_ref * scale_h)
        
        print(f"{label}: Expected at ({x}, {y}) pixels")
        
        # Draw large crosshair
        color = (0, 255, 0)  # Green for expected position
        cv2.line(result, (x-40, y), (x+40, y), color, 3)
        cv2.line(result, (x, y-40), (x, y+40), color, 3)
        cv2.circle(result, (x, y), 60, color, 3)
        
        # Draw label with background
        label_text = f"{label}"
        coord_text = f"({x}, {y})"
        
        # Position label based on corner
        if i == 0:  # Top-Left
            label_pos = (x + 70, y - 20)
            coord_pos = (x + 70, y + 5)
        elif i == 1:  # Top-Right
            label_pos = (x - 350, y - 20)
            coord_pos = (x - 350, y + 5)
        elif i == 2:  # Bottom-Right
            label_pos = (x - 350, y + 20)
            coord_pos = (x - 350, y + 45)
        else:  # Bottom-Left
            label_pos = (x + 70, y + 20)
            coord_pos = (x + 70, y + 45)
        
        # Draw text with black background for readability
        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(result, (label_pos[0]-5, label_pos[1]-th-5), 
                     (label_pos[0]+tw+5, label_pos[1]+10), (0, 0, 0), -1)
        cv2.putText(result, label_text, label_pos, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        (tw2, th2), _ = cv2.getTextSize(coord_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(result, (coord_pos[0]-5, coord_pos[1]-th2-5), 
                     (coord_pos[0]+tw2+5, coord_pos[1]+10), (0, 0, 0), -1)
        cv2.putText(result, coord_text, coord_pos, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Add title and info
    title = "Anchor Position Reference - Expected Locations"
    cv2.rectangle(result, (0, 0), (w, 80), (0, 0, 0), -1)
    cv2.putText(result, title, (20, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    
    info = f"Grid: {grid_size}px (thin), {thick_grid}px (thick) | Green crosshairs = Expected positions"
    cv2.putText(result, info, (20, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    # Determine output path
    if output_path is None:
        input_path = Path(image_path)
        output_path = input_path.parent / f"{input_path.stem}_reference{input_path.suffix}"
    
    # Save result
    cv2.imwrite(str(output_path), result)
    print(f"✓ Reference image saved: {output_path}")
    
    return output_path


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_anchor_reference.py <image> <template>")
        print("Example: python scripts/create_anchor_reference.py page_0001_anchors.png template.json")
        sys.exit(1)
    
    image_path = sys.argv[1]
    template_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = create_anchor_reference_image(image_path, template_path, output_path)
    sys.exit(0 if result else 1)
