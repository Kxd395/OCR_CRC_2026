#!/usr/bin/env python3
import argparse, numpy as np, cv2, json
from scripts.common import read_json, latest_run_dir, sorted_pages, tpl_size, roi_to_poly, apply_h

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    args = ap.parse_args()

    tpl = read_json(args.template); tpl_w, tpl_h = tpl_size(tpl)
    latest = latest_run_dir("artifacts")
    images_dir = latest/"step2_alignment_and_crop"/"aligned_cropped"
    logs_dir = latest/"logs"
    
    # Create step5 output directory
    step5_dir = latest/"step5_qa_overlays"
    step5_dir.mkdir(exist_ok=True)

    results = read_json(latest/"step4_ocr_results"/"results.json")
    hmap = read_json(logs_dir/"homography.json")
    state = {r["page"]: {b["id"]: b for b in r["checkboxes"]} for r in results}
    rois = tpl.get("checkbox_rois_norm", [])

    for img_path in sorted_pages(images_dir):
        img = cv2.imread(str(img_path)); ov = img.copy()
        img_h, img_w = img.shape[:2]
        
        for r in rois:
            # Draw directly on cropped image using normalized coordinates
            x = int(r['x'] * img_w)
            y = int(r['y'] * img_h)
            w = int(r['w'] * img_w)
            h = int(r['h'] * img_h)
            
            # Get checkbox state
            box_state = state.get(img_path.name, {}).get(r["id"], {})
            checked = box_state.get("checked", False)
            score = box_state.get("score", 0.0)
            
            # Color code: Green for checked, Orange for unchecked
            color = (50, 205, 50) if checked else (255, 165, 0)  # Green or Orange
            thickness = 3 if checked else 2
            
            cv2.rectangle(ov, (x, y), (x+w, y+h), color, thickness)
            
            # Add score label near the checkbox
            label = f"{score*100:.1f}%"
            cv2.putText(ov, label, (x - 20, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
        
        cv2.imwrite(str(step5_dir/f"{img_path.stem}_qa.png"), ov)

if __name__=="__main__":
    main()
