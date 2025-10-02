#!/usr/bin/env python3
"""
Show what each checkbox ID represents and create a visual guide
"""
import cv2
import numpy as np
import json
from pathlib import Path

def main():
    # Load template
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    with open(template_path) as f:
        template = json.load(f)
    
    print("="*70)
    print("CHECKBOX ID EXPLANATION")
    print("="*70)
    
    print("\nThe checkbox IDs represent a 5×5 grid:")
    print("\n  Q1 = Question/Row 1 (top row)")
    print("  Q2 = Question/Row 2")
    print("  Q3 = Question/Row 3")
    print("  Q4 = Question/Row 4")
    print("  Q5 = Question/Row 5 (bottom row)")
    
    print("\n  _0, _1, _2, _3, _4 = Columns (left to right)")
    print("    _0 = Leftmost checkbox")
    print("    _4 = Rightmost checkbox")
    
    print("\n" + "="*70)
    print("GRID LAYOUT")
    print("="*70)
    print("\n          Col 0    Col 1    Col 2    Col 3    Col 4")
    print("          (Left)                           (Right)")
    print("       ┌─────────┬────────┬────────┬────────┬─────────┐")
    print("Row 1  │  Q1_0   │  Q1_1  │  Q1_2  │  Q1_3  │  Q1_4   │")
    print("(Top)  ├─────────┼────────┼────────┼────────┼─────────┤")
    print("Row 2  │  Q2_0   │  Q2_1  │  Q2_2  │  Q2_3  │  Q2_4   │")
    print("       ├─────────┼────────┼────────┼────────┼─────────┤")
    print("Row 3  │  Q3_0   │  Q3_1  │  Q3_2  │  Q3_3  │  Q3_4   │")
    print("       ├─────────┼────────┼────────┼────────┼─────────┤")
    print("Row 4  │  Q4_0   │  Q4_1  │  Q4_2  │  Q4_3  │  Q4_4   │")
    print("       ├─────────┼────────┼────────┼────────┼─────────┤")
    print("Row 5  │  Q5_0   │  Q5_1  │  Q5_2  │  Q5_3  │  Q5_4   │")
    print("(Bot)  └─────────┴────────┴────────┴────────┴─────────┘")
    
    print("\n" + "="*70)
    print("EXAMPLE: If you filled in...")
    print("="*70)
    print("\n  Q1_2 = Row 1 (top), Column 2 (middle)")
    print("  Q3_4 = Row 3 (middle), Column 4 (rightmost)")
    print("  Q5_0 = Row 5 (bottom), Column 0 (leftmost)")
    
    print("\n" + "="*70)
    print("DETECTION PROCESS")
    print("="*70)
    print("\nFor EACH checkbox:")
    print("  1. Extract the checkbox region (120×110 pixels)")
    print("  2. Convert to binary (black/white)")
    print("  3. Count black pixels")
    print("  4. Calculate fill percentage")
    print("  5. Compare to threshold:")
    print("     - If fill% >= threshold → CHECKED ✅")
    print("     - If fill% < threshold → UNCHECKED ❌")
    
    print("\n" + "="*70)
    print("YOUR CURRENT SETUP")
    print("="*70)
    print(f"\nTotal checkboxes per page: {len(template['checkbox_rois_norm'])}")
    print("Grid: 5 rows × 5 columns = 25 checkboxes")
    
    # Show actual template IDs
    print("\nCheckbox IDs in template:")
    for i, roi in enumerate(template['checkbox_rois_norm']):
        if i % 5 == 0:
            print()
        print(f"  {roi['id']}", end="")
    print("\n")
    
    # Load a sample image and create visual guide
    run_dir = Path("artifacts/run_20251001_185300")
    img_path = run_dir / "02_step2_alignment_and_crop/aligned_cropped/page_0013_aligned_cropped.png"
    
    if img_path.exists():
        img = cv2.imread(str(img_path))
        h, w = img.shape[:2]
        
        # Create annotated image
        annotated = img.copy()
        
        # Draw grid lines and labels
        for i, roi in enumerate(template['checkbox_rois_norm']):
            x = int(roi['x'] * w)
            y = int(roi['y'] * h)
            roi_w = int(roi['w'] * w)
            roi_h = int(roi['h'] * h)
            
            # Get row and column
            row = i // 5 + 1
            col = i % 5
            
            # Color code by row
            colors = [
                (0, 0, 255),    # Red - Row 1
                (0, 165, 255),  # Orange - Row 2
                (0, 255, 255),  # Yellow - Row 3
                (0, 255, 0),    # Green - Row 4
                (255, 0, 255)   # Magenta - Row 5
            ]
            color = colors[row - 1]
            
            # Draw rectangle
            cv2.rectangle(annotated, (x, y), (x+roi_w, y+roi_h), color, 3)
            
            # Add large label
            label = roi['id']
            font_scale = 0.8
            thickness = 2
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
            
            # Center text in box
            text_x = x + (roi_w - text_size[0]) // 2
            text_y = y + (roi_h + text_size[1]) // 2
            
            # White background
            cv2.rectangle(annotated, (text_x-5, text_y-text_size[1]-5),
                         (text_x+text_size[0]+5, text_y+5), (255, 255, 255), -1)
            
            # Black text
            cv2.putText(annotated, label, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
        
        # Add legend
        legend_height = 200
        legend = np.ones((legend_height, w, 3), dtype=np.uint8) * 255
        
        cv2.putText(legend, "CHECKBOX ID GUIDE", (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        
        y_pos = 70
        legend_items = [
            ((0, 0, 255), "Row 1 (Q1): Top row"),
            ((0, 165, 255), "Row 2 (Q2)"),
            ((0, 255, 255), "Row 3 (Q3): Middle row"),
            ((0, 255, 0), "Row 4 (Q4)"),
            ((255, 0, 255), "Row 5 (Q5): Bottom row")
        ]
        
        for color, text in legend_items:
            cv2.rectangle(legend, (20, y_pos-15), (50, y_pos), color, -1)
            cv2.putText(legend, text, (60, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            y_pos += 25
        
        cv2.putText(legend, "Columns: _0 (left) to _4 (right)", (400, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Combine
        result = np.vstack([annotated, legend])
        
        # Save
        output_path = run_dir / "CHECKBOX_ID_GUIDE.png"
        cv2.imwrite(str(output_path), result)
        
        print("="*70)
        print("VISUAL GUIDE CREATED")
        print("="*70)
        print(f"\n✅ Saved visual guide: {output_path}")
        print(f"\nTo view:")
        print(f"  open {output_path}")
        print("\nThis shows exactly which ID corresponds to which checkbox position!")

if __name__ == "__main__":
    main()
