#!/usr/bin/env python3
"""
Run checkbox detection with adjustable threshold
"""
import cv2
import numpy as np
import json
from pathlib import Path
import sys

def detect_checkbox(img_gray, x, y, w, h):
    """Detect checkbox using Otsu thresholding"""
    checkbox = img_gray[y:y+h, x:x+w]
    _, binary = cv2.threshold(checkbox, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    fill_pct = (np.sum(binary == 255) / binary.size) * 100
    return fill_pct

def main():
    if len(sys.argv) < 3:
        print("Usage: python rerun_detection_with_threshold.py <run_directory> <threshold>")
        print("Example: python rerun_detection_with_threshold.py artifacts/run_20251001_185300 25")
        sys.exit(1)
    
    run_dir = Path(sys.argv[1])
    threshold = float(sys.argv[2])
    
    print("="*70)
    print(f"CHECKBOX DETECTION WITH THRESHOLD: {threshold}%")
    print("="*70)
    
    # Load template
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    with open(template_path) as f:
        template = json.load(f)
    
    # Find all aligned cropped images
    aligned_dir = run_dir / "02_step2_alignment_and_crop/aligned_cropped"
    image_files = sorted(aligned_dir.glob("page_*.png"))
    
    print(f"\nProcessing {len(image_files)} pages...")
    print(f"Detection threshold: {threshold}%\n")
    
    # Process all pages
    all_results = []
    total_checked = 0
    total_boxes = 0
    
    for img_path in image_files:
        page_num = img_path.stem.split('_')[1]
        
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = img_gray.shape
        
        page_result = {
            'page': f"page_{page_num}",
            'checkboxes': [],
            'checked_count': 0
        }
        
        for roi in template['checkbox_rois_norm']:
            x = int(roi['x'] * w)
            y = int(roi['y'] * h)
            roi_w = int(roi['w'] * w)
            roi_h = int(roi['h'] * h)
            
            if x < 0 or y < 0 or x+roi_w > w or y+roi_h > h:
                continue
            
            fill_pct = detect_checkbox(img_gray, x, y, roi_w, roi_h)
            is_checked = fill_pct >= threshold
            
            if is_checked:
                page_result['checked_count'] += 1
                total_checked += 1
            
            total_boxes += 1
            
            page_result['checkboxes'].append({
                'id': roi['id'],
                'fill': round(fill_pct, 2),
                'checked': bool(is_checked)
            })
        
        all_results.append(page_result)
        
        # Print summary for pages with checked boxes
        if page_result['checked_count'] > 0:
            print(f"Page {page_num}: {page_result['checked_count']} checked boxes")
            for cb in page_result['checkboxes']:
                if cb['checked']:
                    print(f"  ✅ {cb['id']}: {cb['fill']}%")
    
    # Save results
    output_path = run_dir / f"detection_results_threshold_{int(threshold)}.json"
    with open(output_path, 'w') as f:
        json.dump({
            'threshold': threshold,
            'total_pages': len(image_files),
            'total_boxes': total_boxes,
            'total_checked': total_checked,
            'pages': all_results
        }, f, indent=2)
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Threshold: {threshold}%")
    print(f"Total pages: {len(image_files)}")
    print(f"Total checkboxes: {total_boxes}")
    print(f"Checked boxes: {total_checked} ({total_checked/total_boxes*100:.1f}%)")
    print(f"Empty boxes: {total_boxes-total_checked} ({(total_boxes-total_checked)/total_boxes*100:.1f}%)")
    print(f"\n✅ Results saved to: {output_path}")
    
    # Pages with filled boxes
    pages_with_checks = [p for p in all_results if p['checked_count'] > 0]
    if pages_with_checks:
        print(f"\nPages with checked boxes: {len(pages_with_checks)}")
        for page in pages_with_checks:
            print(f"  - {page['page']}: {page['checked_count']} boxes")

if __name__ == "__main__":
    main()
