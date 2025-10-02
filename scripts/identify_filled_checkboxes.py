#!/usr/bin/env python3
"""
Identify filled checkboxes on a specific page and create annotated image
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
    page_num = sys.argv[1] if len(sys.argv) > 1 else "0013"
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 25.0
    
    run_dir = Path("artifacts/run_20251001_185300")
    
    print("="*70)
    print(f"IDENTIFYING FILLED CHECKBOXES - PAGE {page_num}")
    print(f"Detection Threshold: {threshold}%")
    print("="*70)
    
    # Load template
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    with open(template_path) as f:
        template = json.load(f)
    
    # Load image
    img_path = run_dir / f"02_step2_alignment_and_crop/aligned_cropped/page_{page_num}_aligned_cropped.png"
    if not img_path.exists():
        print(f"Error: Image not found at {img_path}")
        sys.exit(1)
    
    img = cv2.imread(str(img_path))
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = img_gray.shape
    
    # Create annotated image
    annotated = img.copy()
    
    # Analyze all checkboxes
    print("\nCheckbox Analysis:")
    print("="*70)
    print(f"{'ID':<10} {'Row':<6} {'Col':<6} {'Fill %':<10} {'Status':<12}")
    print("="*70)
    
    filled_boxes = []
    empty_boxes = []
    
    for i, roi in enumerate(template['checkbox_rois_norm']):
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        if x < 0 or y < 0 or x+roi_w > w or y+roi_h > h:
            continue
        
        fill_pct = detect_checkbox(img_gray, x, y, roi_w, roi_h)
        is_checked = fill_pct >= threshold
        
        # Get row and column (1-based for display)
        row = i // 5 + 1
        col = i % 5 + 1
        
        # Determine color and thickness
        if is_checked:
            color = (0, 0, 255)  # Red for checked
            thickness = 4
            status = "✅ CHECKED"
            filled_boxes.append(roi['id'])
        else:
            color = (128, 128, 128)  # Gray for empty
            thickness = 2
            status = "❌ empty"
            empty_boxes.append(roi['id'])
        
        # Draw rectangle
        cv2.rectangle(annotated, (x, y), (x+roi_w, y+roi_h), color, thickness)
        
        # Add ID label
        cv2.putText(annotated, roi['id'], (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Add fill percentage inside box
        fill_text = f"{fill_pct:.0f}%"
        text_size = cv2.getTextSize(fill_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        text_x = x + (roi_w - text_size[0]) // 2
        text_y = y + (roi_h + text_size[1]) // 2
        
        # White background for text
        cv2.rectangle(annotated, (text_x-3, text_y-text_size[1]-3),
                     (text_x+text_size[0]+3, text_y+3), (255, 255, 255), -1)
        cv2.putText(annotated, fill_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Print status
        print(f"{roi['id']:<10} {row:<6} {col:<6} {fill_pct:<10.1f} {status:<12}")
    
    # Add legend
    legend_height = 250
    legend = np.ones((legend_height, w, 3), dtype=np.uint8) * 255
    
    # Title
    cv2.putText(legend, f"Page {page_num} - Checkbox Detection Results", (20, 35),
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    
    # Summary
    y_pos = 80
    cv2.putText(legend, f"Detection Threshold: {threshold}%", (20, y_pos),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    y_pos += 35
    
    cv2.rectangle(legend, (20, y_pos-20), (50, y_pos-5), (0, 0, 255), -1)
    cv2.putText(legend, f"CHECKED (fill >= {threshold}%): {len(filled_boxes)} boxes", (60, y_pos-5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    y_pos += 35
    
    cv2.rectangle(legend, (20, y_pos-20), (50, y_pos-5), (128, 128, 128), -1)
    cv2.putText(legend, f"EMPTY (fill < {threshold}%): {len(empty_boxes)} boxes", (60, y_pos-5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    y_pos += 40
    
    # List filled boxes
    if filled_boxes:
        cv2.putText(legend, "Filled Checkboxes:", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y_pos += 30
        
        filled_text = ", ".join(filled_boxes)
        cv2.putText(legend, filled_text, (40, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    else:
        cv2.putText(legend, "No filled checkboxes detected", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 1)
    
    # Combine
    result = np.vstack([annotated, legend])
    
    # Save
    output_path = run_dir / f"page_{page_num}_IDENTIFIED.png"
    cv2.imwrite(str(output_path), result)
    
    print("="*70)
    print("\nSUMMARY")
    print("="*70)
    print(f"Total checkboxes: 25")
    print(f"Filled checkboxes: {len(filled_boxes)}")
    print(f"Empty checkboxes: {len(empty_boxes)}")
    
    if filled_boxes:
        print(f"\n✅ FILLED CHECKBOXES:")
        for cb_id in filled_boxes:
            # Convert ID to row/col
            idx = int(cb_id.split('_')[0][1]) - 1  # Q1->0, Q2->1, etc
            row = idx + 1
            col = int(cb_id.split('_')[1]) + 1  # 0->1, 1->2, etc
            print(f"   {cb_id} (Row {row}, Column {col})")
    
    print(f"\n{'='*70}")
    print(f"✅ Annotated image saved: {output_path}")
    print(f"\nTo view:")
    print(f"  open {output_path}")

if __name__ == "__main__":
    main()
