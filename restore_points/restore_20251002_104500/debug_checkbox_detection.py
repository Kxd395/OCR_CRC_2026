#!/usr/bin/env python3
"""
Debug checkbox detection by extracting ROIs and showing their contents
"""
import cv2
import numpy as np
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_checkbox_detection.py <run_directory>")
        sys.exit(1)
    
    run_dir = Path(sys.argv[1])
    
    # Load the aligned cropped image
    img_path = run_dir / "02_step2_alignment_and_crop/aligned_cropped/page_0001_aligned_cropped.png"
    if not img_path.exists():
        print(f"Error: Image not found at {img_path}")
        sys.exit(1)
    
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"Error: Could not load image from {img_path}")
        sys.exit(1)
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = img_gray.shape
    print(f"Image dimensions: {w}×{h}")
    
    # Load template
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    with open(template_path) as f:
        template = json.load(f)
    
    # Create output directory
    debug_dir = run_dir / "debug_checkboxes"
    debug_dir.mkdir(exist_ok=True)
    
    print(f"\nExtracting first 5 checkboxes from Q1:")
    
    for i, roi in enumerate(template['checkbox_rois_norm'][:5]):
        roi_id = roi['id']
        
        # Convert normalized coords to pixels
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        print(f"\n{roi_id}:")
        print(f"  Normalized: x={roi['x']:.4f}, y={roi['y']:.4f}, w={roi['w']:.4f}, h={roi['h']:.4f}")
        print(f"  Pixels: x={x}, y={y}, w={roi_w}, h={roi_h}")
        
        # Extract ROI
        if x < 0 or y < 0 or x+roi_w > w or y+roi_h > h:
            print(f"  ⚠️  WARNING: ROI extends outside image bounds!")
            continue
        
        checkbox = img_gray[y:y+roi_h, x:x+roi_w]
        
        # Calculate fill percentage
        _, binary = cv2.threshold(checkbox, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        fill_pct = (np.sum(binary == 255) / binary.size) * 100
        
        # Stats
        mean_val = np.mean(checkbox)
        std_val = np.std(checkbox)
        
        print(f"  Mean intensity: {mean_val:.1f}")
        print(f"  Std dev: {std_val:.1f}")
        print(f"  Fill percentage: {fill_pct:.1f}%")
        print(f"  Status: {'CHECKED' if fill_pct >= 55 else 'UNCHECKED'}")
        
        # Save checkbox image
        output_path = debug_dir / f"{roi_id}_fill{fill_pct:.0f}pct.png"
        
        # Create a visualization with the checkbox and its binary version
        vis = np.hstack([
            cv2.cvtColor(checkbox, cv2.COLOR_GRAY2BGR),
            cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        ])
        
        # Add text
        cv2.putText(vis, f"{fill_pct:.1f}%", (5, 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imwrite(str(output_path), vis)
        print(f"  Saved: {output_path.name}")
    
    # Create a composite image showing all ROIs with their positions
    print(f"\n\nCreating composite visualization...")
    composite = img.copy()
    
    for roi in template['checkbox_rois_norm']:
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        # Draw rectangle
        cv2.rectangle(composite, (x, y), (x+roi_w, y+roi_h), (0, 255, 0), 2)
        
        # Add label
        cv2.putText(composite, roi['id'], (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    composite_path = debug_dir / "all_rois_on_image.png"
    cv2.imwrite(str(composite_path), composite)
    print(f"Saved composite: {composite_path}")
    
    print(f"\n✅ Debug images saved to: {debug_dir}")
    print(f"\nNext steps:")
    print(f"1. Open {debug_dir} to view extracted checkboxes")
    print(f"2. Check if the green boxes in all_rois_on_image.png align with actual checkboxes")
    print(f"3. If boxes are misaligned, coordinates need adjustment")

if __name__ == "__main__":
    main()
