#!/usr/bin/env python3
"""
Update template.json with measured checkbox coordinates.

Based on measurements from checkbox coordinate documentation:
- Image dimensions: 2267×2813 pixels (aligned_cropped)
- Checkbox dimensions: 120×110 pixels
- Measured pixel coordinates converted to normalized (0.0-1.0)
"""

import json
import sys
from pathlib import Path

# Image dimensions (aligned_cropped)
IMAGE_WIDTH = 2267
IMAGE_HEIGHT = 2813

# Checkbox dimensions
BOX_WIDTH = 120
BOX_HEIGHT = 110

# Measured X coordinates (left edge of boxes)
X_COORDS = [280, 690, 1100, 1505, 1915]

# Measured Y coordinates (top edge of boxes)
Y_COORDS = [1228, 1500, 1772, 2044, 2316]

def pixel_to_normalized(pixel, dimension):
    """Convert pixel coordinate to normalized (0.0-1.0)."""
    return round(pixel / dimension, 4)

def generate_checkbox_rois():
    """Generate all 25 checkbox ROIs with normalized coordinates."""
    rois = []
    
    # Generate for each row (Q1-Q5)
    for q_idx, y_pixel in enumerate(Y_COORDS, start=1):
        # Generate for each box (0-4)
        for box_idx, x_pixel in enumerate(X_COORDS):
            # Calculate normalized coordinates
            x_norm = pixel_to_normalized(x_pixel, IMAGE_WIDTH)
            y_norm = pixel_to_normalized(y_pixel, IMAGE_HEIGHT)
            w_norm = pixel_to_normalized(BOX_WIDTH, IMAGE_WIDTH)
            h_norm = pixel_to_normalized(BOX_HEIGHT, IMAGE_HEIGHT)
            
            roi = {
                "id": f"Q{q_idx}_{box_idx}",
                "x": x_norm,
                "y": y_norm,
                "w": w_norm,
                "h": h_norm
            }
            rois.append(roi)
    
    return rois

def update_template(template_path, output_path=None):
    """Update template.json with new checkbox coordinates."""
    # Read existing template
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    # Generate new checkbox ROIs
    new_rois = generate_checkbox_rois()
    
    # Update template
    template['checkbox_rois_norm'] = new_rois
    template['version'] = "1.1.0"  # Increment version
    
    # Add measurement metadata
    if 'metadata' not in template:
        template['metadata'] = {}
    
    template['metadata']['coordinate_measurement'] = {
        "date": "2025-10-01",
        "method": "grid_overlay_measurement",
        "image_dimensions": {
            "width_px": IMAGE_WIDTH,
            "height_px": IMAGE_HEIGHT
        },
        "checkbox_dimensions": {
            "width_px": BOX_WIDTH,
            "height_px": BOX_HEIGHT
        },
        "x_coordinates_px": X_COORDS,
        "y_coordinates_px": Y_COORDS,
        "reference": "docs/CHECKBOX_COORDINATES.md"
    }
    
    # Write updated template
    if output_path is None:
        output_path = template_path
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ Template updated successfully: {output_path}")
    print(f"   Version: {template['version']}")
    print(f"   Checkboxes: {len(new_rois)}")
    print(f"\nSample coordinates (Q1_0):")
    print(f"   Pixel: ({X_COORDS[0]}, {Y_COORDS[0]}) → ({X_COORDS[0]+BOX_WIDTH}, {Y_COORDS[0]+BOX_HEIGHT})")
    print(f"   Normalized: ({new_rois[0]['x']}, {new_rois[0]['y']}) → width={new_rois[0]['w']}, height={new_rois[0]['h']}")
    
    return template

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python update_template_coordinates.py <template_path> [output_path]")
        print("\nExample:")
        print("  python update_template_coordinates.py templates/crc_survey_l_anchors_v1/template.json")
        print("\nTo create new version:")
        print("  python update_template_coordinates.py templates/crc_survey_l_anchors_v1/template.json templates/crc_survey_l_anchors_v1/template_v1.1.json")
        sys.exit(1)
    
    template_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(template_path).exists():
        print(f"❌ Error: Template file not found: {template_path}")
        sys.exit(1)
    
    update_template(template_path, output_path)

if __name__ == "__main__":
    main()
