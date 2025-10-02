#!/usr/bin/env python3
"""
Create overlay visualizations for all pages showing checkbox ROIs
"""
import cv2
import numpy as np
import json
import sys
from pathlib import Path

def create_overlay_for_page(img_path, template, output_path):
    """Create an overlay showing all checkbox ROIs on one page"""
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"  ⚠️  Could not load {img_path.name}")
        return False
    
    h, w = img.shape[:2]
    overlay = img.copy()
    
    # Draw all checkbox ROIs
    for roi in template['checkbox_rois_norm']:
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        # Draw green rectangle
        cv2.rectangle(overlay, (x, y), (x+roi_w, y+roi_h), (0, 255, 0), 2)
        
        # Add label
        cv2.putText(overlay, roi['id'], (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imwrite(str(output_path), overlay)
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_all_overlays.py <run_directory>")
        sys.exit(1)
    
    run_dir = Path(sys.argv[1])
    
    # Load template
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)
    
    with open(template_path) as f:
        template = json.load(f)
    
    print(f"Loaded template with {len(template['checkbox_rois_norm'])} checkbox ROIs")
    
    # Find all aligned cropped images
    aligned_dir = run_dir / "02_step2_alignment_and_crop/aligned_cropped"
    if not aligned_dir.exists():
        print(f"Error: Aligned images directory not found at {aligned_dir}")
        sys.exit(1)
    
    image_files = sorted(aligned_dir.glob("page_*.png"))
    if not image_files:
        print(f"Error: No page images found in {aligned_dir}")
        sys.exit(1)
    
    print(f"Found {len(image_files)} pages to process")
    
    # Create output directory
    output_dir = run_dir / "checkbox_overlays"
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Process all pages
    success_count = 0
    for img_path in image_files:
        page_name = img_path.stem  # e.g., "page_0001_aligned_cropped"
        page_num = page_name.split('_')[1]  # e.g., "0001"
        output_path = output_dir / f"page_{page_num}_overlay.png"
        
        print(f"Processing {img_path.name}...", end=" ")
        if create_overlay_for_page(img_path, template, output_path):
            print(f"✅ Saved to {output_path.name}")
            success_count += 1
        else:
            print("❌ Failed")
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully processed {success_count}/{len(image_files)} pages")
    print(f"📁 Overlays saved to: {output_dir}")
    print(f"\nTo view all overlays:")
    print(f"  open {output_dir}")
    print(f"\nTo view first page:")
    print(f"  open {output_dir}/page_0001_overlay.png")

if __name__ == "__main__":
    main()
