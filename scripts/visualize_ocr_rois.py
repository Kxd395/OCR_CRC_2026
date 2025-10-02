#!/usr/bin/env python3
"""
Create visual overlay showing OCR-detected checkbox ROIs on the image.
This helps verify if the template coordinates are correctly aligned.
"""

import json
import cv2
import numpy as np
from pathlib import Path
import sys

def draw_checkbox_overlays(image_path, template_path, output_path, results_path=None):
    """Draw checkbox ROIs from template on image with detection scores."""
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"❌ Error: Could not load image: {image_path}")
        return False
    
    h, w = img.shape[:2]
    print(f"Image size: {w}×{h}")
    
    # Load template
    with open(template_path, 'r') as f:
        template = json.load(f)
    
    checkbox_rois = template['checkbox_rois_norm']
    print(f"Template checkboxes: {len(checkbox_rois)}")
    
    # Load results if available
    results = None
    if results_path and Path(results_path).exists():
        with open(results_path, 'r') as f:
            data = json.load(f)
            page_name = Path(image_path).name
            # Find matching page in results
            for page in data:
                if page['page'] == page_name:
                    results = {cb['id']: cb for cb in page['checkboxes']}
                    break
    
    # Create overlay
    overlay = img.copy()
    
    # Draw each checkbox ROI
    for roi in checkbox_rois:
        # Convert normalized coordinates to pixels
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        box_w = int(roi['w'] * w)
        box_h = int(roi['h'] * h)
        
        # Get results if available
        score = None
        checked = False
        if results and roi['id'] in results:
            score = results[roi['id']]['score']
            checked = results[roi['id']]['checked']
        
        # Color based on score/status
        if checked:
            color = (0, 255, 0)  # Green for checked
            thickness = 3
        elif score is not None:
            # Color gradient based on score
            if score >= 0.55:
                color = (0, 200, 255)  # Orange (high score but not checked)
            elif score >= 0.20:
                color = (0, 165, 255)  # Orange-yellow
            else:
                color = (255, 0, 0)  # Blue for low score
            thickness = 2
        else:
            color = (128, 128, 128)  # Gray if no results
            thickness = 2
        
        # Draw rectangle
        cv2.rectangle(overlay, (x, y), (x + box_w, y + box_h), color, thickness)
        
        # Add label with ID and score
        label = roi['id']
        if score is not None:
            label += f"\n{score:.3f}"
        
        # Add text background for readability
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        font_thickness = 1
        
        # Split label for multi-line
        lines = label.split('\n')
        y_offset = y - 5
        
        for line in lines:
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            # Draw background
            cv2.rectangle(overlay, 
                         (x, y_offset - text_size[1] - 2), 
                         (x + text_size[0] + 4, y_offset + 2),
                         (255, 255, 255), -1)
            # Draw text
            cv2.putText(overlay, line, (x + 2, y_offset), 
                       font, font_scale, (0, 0, 0), font_thickness)
            y_offset -= text_size[1] + 4
    
    # Add legend
    legend_y = 30
    cv2.putText(overlay, "Legend:", (10, legend_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(overlay, "Legend:", (10, legend_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    legend_items = [
        ("Green: Checked (score >= 0.55)", (0, 255, 0)),
        ("Orange: High score (0.20-0.54)", (0, 165, 255)),
        ("Blue: Low score (< 0.20)", (255, 0, 0))
    ]
    
    for i, (text, color) in enumerate(legend_items):
        y = legend_y + (i + 1) * 25
        cv2.rectangle(overlay, (10, y - 15), (30, y - 5), color, -1)
        cv2.putText(overlay, text, (40, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(overlay, text, (40, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Save
    cv2.imwrite(str(output_path), overlay)
    print(f"✅ Overlay saved: {output_path}")
    
    return True

def main():
    """Main function."""
    if len(sys.argv) < 4:
        print("Usage: python visualize_ocr_rois.py <image_path> <template_path> <output_path> [results_path]")
        print("\nExample:")
        print("  python visualize_ocr_rois.py \\")
        print("    artifacts/run_20251001_185300/aligned_cropped/page_0001_aligned_cropped.png \\")
        print("    templates/crc_survey_l_anchors_v1/template.json \\")
        print("    artifacts/run_20251001_185300/ocr_roi_overlay.png \\")
        print("    artifacts/run_20251001_185300/logs/ocr_results.json")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    template_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    results_path = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    
    if not image_path.exists():
        print(f"❌ Error: Image not found: {image_path}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"❌ Error: Template not found: {template_path}")
        sys.exit(1)
    
    draw_checkbox_overlays(image_path, template_path, output_path, results_path)

if __name__ == "__main__":
    main()
