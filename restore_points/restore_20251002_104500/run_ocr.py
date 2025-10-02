#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, numpy as np, cv2, pytesseract, yaml
from scripts.common import read_json, write_json_atomic, latest_run_dir, sorted_pages, tpl_size

def roi_crop(img, roi, tpl_w, tpl_h, min_margin):
    x = int(roi["x"]*tpl_w) + min_margin
    y = int(roi["y"]*tpl_h) + min_margin
    w = int(roi["w"]*tpl_w) - 2*min_margin
    h = int(roi["h"]*tpl_h) - 2*min_margin
    x = max(0, x); y = max(0, y); w = max(1, w); h = max(1, h)
    return img[y:y+h, x:x+w]

def mean_fill(gray_roi):
    norm = gray_roi.astype(np.float32)/255.0
    return float((1.0 - norm).mean())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--threshold", type=float, default=None,
                   help="Checkbox fill threshold (0-100%%). Overrides config/template. Default: from config or template.")
    args = ap.parse_args()

    tpl = read_json(args.template)
    rois = tpl.get("checkbox_rois_norm", [])
    tpl_w, tpl_h = tpl_size(tpl)

    latest = latest_run_dir("artifacts")
    images_dir = latest/"step2_alignment_and_crop"/"aligned_cropped"
    logs_dir = latest/"logs"
    
    # Create step4 output directory
    step4_dir = latest/"step4_ocr_results"
    step4_dir.mkdir(exist_ok=True)

    cfg = yaml.safe_load(open("configs/ocr.yaml")) or {}
    langs = "+".join((cfg.get("tesseract_langs") or ["eng"]))
    
    # Threshold priority: CLI arg > template > config > default
    if args.threshold is not None:
        fill_th = args.threshold / 100.0  # Convert percentage to decimal
    elif "detection_settings" in tpl and "fill_threshold_percent" in tpl["detection_settings"]:
        fill_th = tpl["detection_settings"]["fill_threshold_percent"] / 100.0
    else:
        fill_th = float((cfg.get("checkbox") or {}).get("fill_threshold", 0.115))
    
    min_margin = int((cfg.get("checkbox") or {}).get("min_margin", 2))
    
    print(f"Using fill threshold: {fill_th*100:.1f}%")

    out_pages = []
    for img_path in sorted_pages(images_dir):
        img = cv2.imread(str(img_path)); gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Use cropped image dimensions directly (no homography warp)
        img_h, img_w = gray.shape[:2]

        text = pytesseract.image_to_string(gray, lang=langs)

        boxes = []; filled = 0
        for r in rois:
            # Extract checkbox directly from cropped image using normalized coordinates
            x = int(r["x"] * img_w) + min_margin
            y = int(r["y"] * img_h) + min_margin
            w = int(r["w"] * img_w) - 2*min_margin
            h = int(r["h"] * img_h) - 2*min_margin
            x = max(0, x); y = max(0, y); w = max(1, w); h = max(1, h)
            crop = gray[y:y+h, x:x+w]
            
            score = mean_fill(crop); checked = bool(score >= fill_th)
            filled += int(checked)
            boxes.append({"id": r["id"], "score": score, "checked": checked})
        out_pages.append({"page": img_path.name, "text_len": len(text or ""), "checkboxes": boxes, "checkbox_checked_total": filled})

    write_json_atomic(step4_dir/"results.json", out_pages)
    # Also save to logs for backwards compatibility
    write_json_atomic(logs_dir/"ocr_results.json", out_pages)
    with open(logs_dir/"steps.jsonl","a") as f:
        f.write(json.dumps({"step":"ocr","run_dir":str(latest),"pages":len(out_pages)})+"\n")

if __name__=="__main__":
    main()
