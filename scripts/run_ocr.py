#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import pathlib
import numpy as np
import cv2
import yaml
import joblib
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

def extract_checkbox_features(gray_crop):
    """
    Extract 7 features from a checkbox crop for ML classification.
    
    Features match those used in training (extract_features.py):
    1. Fill percentage (baseline - mean darkness)
    2. Edge density (Canny edges)
    3. Stroke length (morphological skeleton)
    4. Corner count (Harris corners)
    5. Connected components (distinct marks)
    6. H/V ratio (horizontal vs vertical edges)
    7. Variance (texture complexity)
    """
    h, w = gray_crop.shape
    
    features = {}
    
    # Feature 1: Fill percentage (current method)
    norm = gray_crop.astype(np.float32) / 255.0
    features['fill_pct'] = float((1.0 - norm).mean()) * 100
    
    # Feature 2: Edge density (Canny)
    edges = cv2.Canny(gray_crop, 50, 150)
    features['edge_density'] = float(edges.sum()) / (w * h * 255) * 100
    
    # Feature 3: Stroke length (morphological skeleton)
    _, binary = cv2.threshold(gray_crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    skeleton = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
    features['stroke_length'] = float(skeleton.sum()) / (w * h * 255) * 100
    
    # Feature 4: Corner count (Harris)
    gray_float = np.float32(gray_crop)
    corners = cv2.cornerHarris(gray_float, 2, 3, 0.04)
    corner_threshold = corners.max() * 0.01 if corners.max() > 0 else 0
    features['corner_count'] = int(np.sum(corners > corner_threshold))
    
    # Feature 5: Connected components
    num_labels, _ = cv2.connectedComponents(binary)
    features['num_components'] = num_labels - 1  # Subtract background
    
    # Feature 6: Horizontal/Vertical ratio
    sobelx = cv2.Sobel(gray_crop, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray_crop, cv2.CV_64F, 0, 1, ksize=3)
    h_energy = float(np.abs(sobelx).sum())
    v_energy = float(np.abs(sobely).sum())
    features['hv_ratio'] = h_energy / (v_energy + 1e-6)
    
    # Feature 7: Variance (texture)
    features['variance'] = float(gray_crop.var())
    
    return features

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

    # Load ML model if available
    model = None
    scaler = None
    use_ml = False
    
    template_dir = pathlib.Path(args.template).parent
    model_file = template_dir / "ml_model.pkl"
    scaler_file = template_dir / "ml_scaler.pkl"
    
    if model_file.exists() and scaler_file.exists():
        try:
            model = joblib.load(model_file)
            scaler = joblib.load(scaler_file)
            use_ml = True
            print("✅ ML model loaded - using edge detection + 7 features")
        except Exception as e:
            print(f"⚠️  Could not load ML model: {e}")
            print("   Falling back to threshold-only detection")
    else:
        print("ℹ️  ML model not found - using threshold-only detection")
    
    feature_names = ['fill_pct', 'edge_density', 'stroke_length', 'corner_count', 
                     'num_components', 'hv_ratio', 'variance']

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
            
            # Use ML model if available, otherwise fall back to threshold
            if model is not None and scaler is not None:
                # Extract features and predict
                features = extract_checkbox_features(crop)
                feature_vector = np.array([[features[name] for name in feature_names]])
                feature_scaled = scaler.transform(feature_vector)
                prediction = model.predict(feature_scaled)[0]
                probability = model.predict_proba(feature_scaled)[0, 1]
                
                checked = bool(prediction == 1)
                score = float(probability)  # Use probability as score
            else:
                # Fallback to threshold-only detection
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
