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

def enhance_checkbox_with_color(img_bgr, x, y, w, h, use_color_fusion=True):
    """
    Extract and enhance checkbox region using multi-channel fusion.
    
    Args:
        img_bgr: Original BGR image
        x, y, w, h: Checkbox ROI coordinates
        use_color_fusion: Whether to use color channel fusion (default: True)
    
    Returns:
        Enhanced grayscale checkbox crop ready for mean_fill()
    """
    # Extract ROI from original BGR image
    roi_bgr = img_bgr[y:y+h, x:x+w]
    
    if not use_color_fusion or len(roi_bgr.shape) != 3:
        # Fallback to grayscale only
        return cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    
    # Check if image is actually color (not grayscale converted to BGR)
    if np.std(roi_bgr) < 1:  # Nearly flat - probably grayscale
        return cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    
    # Split BGR channels
    b, g, r = cv2.split(roi_bgr)
    
    # Convert to grayscale (standard)
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    
    # Blue ink shows strongest in blue channel (B)
    # Black ink shows equally in all channels
    # Pencil/graphite shows best in grayscale
    
    # Take minimum of gray and blue channel (darkest marks win)
    # This enhances both pencil (gray) and blue pen (blue channel)
    fused = np.minimum(gray, b)
    
    return fused

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
    
    # Load per-question thresholds if available
    per_q_thresholds = {}
    if "detection_settings" in tpl and "per_question_thresholds" in tpl["detection_settings"]:
        per_q_thresholds_pct = tpl["detection_settings"]["per_question_thresholds"]
        # Convert from percentage to decimal
        per_q_thresholds = {k: v/100.0 for k, v in per_q_thresholds_pct.items()}
        print(f"Using per-question thresholds: {per_q_thresholds_pct}")
    
    # Load color fusion settings
    use_color_fusion = True  # Default: enabled
    if "detection_settings" in tpl and "use_color_fusion" in tpl["detection_settings"]:
        use_color_fusion = tpl["detection_settings"]["use_color_fusion"]
    print(f"Color channel fusion: {'ENABLED' if use_color_fusion else 'DISABLED (grayscale only)'}")

    out_pages = []
    for img_path in sorted_pages(images_dir):
        img = cv2.imread(str(img_path))
        
        # Use cropped image dimensions directly (no homography warp)
        img_h, img_w = img.shape[:2]

        # Skip slow Tesseract text extraction for faster testing
        # text = pytesseract.image_to_string(gray, lang=langs)
        # text_len = len(text or "")
        text_len = 0

        boxes = []
        filled = 0
        for r in rois:
            # Extract checkbox directly from cropped image using normalized coordinates
            x = int(r["x"] * img_w) + min_margin
            y = int(r["y"] * img_h) + min_margin
            w = int(r["w"] * img_w) - 2*min_margin
            h = int(r["h"] * img_h) - 2*min_margin
            x = max(0, x)
            y = max(0, y)
            w = max(1, w)
            h = max(1, h)
            
            # Apply color channel fusion enhancement
            crop = enhance_checkbox_with_color(img, x, y, w, h, use_color_fusion)
            
            # Get question-specific threshold if available
            question_prefix = r["id"].split("_")[0]  # e.g., "Q1" from "Q1_1"
            threshold = per_q_thresholds.get(question_prefix, fill_th)
            
            score = mean_fill(crop)
            checked = bool(score >= threshold)
            filled += int(checked)
            boxes.append({"id": r["id"], "score": score, "checked": checked})
        out_pages.append({"page": img_path.name, "text_len": text_len, "checkboxes": boxes, "checkbox_checked_total": filled})

    write_json_atomic(step4_dir/"results.json", out_pages)
    # Also save to logs for backwards compatibility
    write_json_atomic(logs_dir/"ocr_results.json", out_pages)
    with open(logs_dir/"steps.jsonl","a") as f:
        f.write(json.dumps({"step":"ocr","run_dir":str(latest),"pages":len(out_pages)})+"\n")

if __name__=="__main__":
    main()
