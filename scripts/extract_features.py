#!/usr/bin/env python3
"""
Extract features from all graded checkboxes for ML training.
Combines fill percentage with edge-based features for improved detection.
"""

import cv2
import numpy as np
import pandas as pd
import json
from pathlib import Path

def extract_checkbox_features(gray_img, x, y, w, h):
    """
    Extract comprehensive features from a checkbox region.
    
    Features:
    1. Fill percentage (baseline - mean darkness)
    2. Edge density (Canny edges)
    3. Stroke length (morphological skeleton)
    4. Corner count (Harris corners)
    5. Connected components (distinct marks)
    6. H/V ratio (horizontal vs vertical edges)
    7. Variance (texture complexity)
    """
    crop = gray_img[y:y+h, x:x+w]
    
    features = {}
    
    # Feature 1: Fill percentage (current method)
    norm = crop.astype(np.float32) / 255.0
    features['fill_pct'] = float((1.0 - norm).mean()) * 100
    
    # Feature 2: Edge density (Canny)
    edges = cv2.Canny(crop, 50, 150)
    features['edge_density'] = float(edges.sum()) / (w * h * 255) * 100
    
    # Feature 3: Stroke length (morphological skeleton)
    _, binary = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    skeleton = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
    features['stroke_length'] = float(skeleton.sum()) / (w * h * 255) * 100
    
    # Feature 4: Corner count (Harris)
    crop_float = np.float32(crop)
    corners = cv2.cornerHarris(crop_float, 2, 3, 0.04)
    corner_threshold = corners.max() * 0.01 if corners.max() > 0 else 0
    features['corner_count'] = int(np.sum(corners > corner_threshold))
    
    # Feature 5: Connected components
    num_labels, _ = cv2.connectedComponents(binary)
    features['num_components'] = num_labels - 1  # Subtract background
    
    # Feature 6: Horizontal/Vertical ratio
    sobelx = cv2.Sobel(crop, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(crop, cv2.CV_64F, 0, 1, ksize=3)
    h_energy = float(np.abs(sobelx).sum())
    v_energy = float(np.abs(sobely).sum())
    features['hv_ratio'] = h_energy / (v_energy + 1e-6)
    
    # Feature 7: Variance (texture)
    features['variance'] = float(crop.var())
    
    return features

def main():
    print("📊 EXTRACTING FEATURES FROM GRADED CHECKBOXES")
    print("=" * 100)
    
    # Load graded data
    graded_file = Path("review/graded log.xlsx")
    if not graded_file.exists():
        print(f"❌ Error: {graded_file} not found!")
        return
    
    df = pd.read_excel(graded_file, sheet_name='Detailed Results + Grading', header=3)
    df = df[df['Actual Marked'].notna()].copy()
    
    print(f"✅ Loaded {len(df)} graded checkboxes")
    
    # Load template
    template_file = Path("templates/crc_survey_l_anchors_v1/template.json")
    with open(template_file) as f:
        tpl = json.load(f)
    
    rois_dict = {roi['id']: roi for roi in tpl['checkbox_rois_norm']}
    
    # Extract features from all checkboxes
    images_dir = Path("artifacts/run_20251002_154502_11.6/step2_alignment_and_crop/aligned_cropped")
    
    all_features = []
    
    print(f"\nProcessing {len(df)} checkboxes...")
    
    for idx, row in df.iterrows():
        page_name = row['Page'].replace('Page ', 'page_') + "_aligned_cropped.png"
        img_path = images_dir / page_name
        
        if not img_path.exists():
            print(f"⚠️  Skipping {page_name} - not found")
            continue
        
        # Load image
        img = cv2.imread(str(img_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Get ROI
        checkbox_id = row['Checkbox ID']
        if checkbox_id not in rois_dict:
            print(f"⚠️  Skipping {checkbox_id} - not in template")
            continue
        
        roi = rois_dict[checkbox_id]
        
        # Calculate coordinates
        x = int(roi['x'] * gray.shape[1])
        y = int(roi['y'] * gray.shape[0])
        w = int(roi['w'] * gray.shape[1])
        h = int(roi['h'] * gray.shape[0])
        
        # Extract features
        feats = extract_checkbox_features(gray, x, y, w, h)
        
        # Add metadata
        feats['page'] = row['Page']
        feats['checkbox_id'] = checkbox_id
        feats['label'] = 1 if row['Actual Marked'] == '✓ Checked' else 0
        
        all_features.append(feats)
        
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(df)} checkboxes...")
    
    print(f"\n✅ Extracted features from {len(all_features)} checkboxes")
    
    # Save to JSON
    output_file = Path("data/features.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(all_features, f, indent=2)
    
    print(f"✅ Saved to {output_file}")
    
    # Show statistics
    df_features = pd.DataFrame(all_features)
    
    print(f"\n📈 FEATURE STATISTICS:")
    print("=" * 100)
    
    checked = df_features[df_features['label'] == 1]
    unchecked = df_features[df_features['label'] == 0]
    
    print(f"\nChecked boxes: {len(checked)}")
    print(f"Unchecked boxes: {len(unchecked)}")
    
    print(f"\n{'Feature':<20} {'Checked Mean':<15} {'Unchecked Mean':<15} {'Separation'}")
    print("-" * 70)
    
    for feat in ['fill_pct', 'edge_density', 'stroke_length', 'corner_count', 
                 'num_components', 'hv_ratio', 'variance']:
        c_mean = checked[feat].mean()
        u_mean = unchecked[feat].mean()
        sep = abs(c_mean - u_mean) / (c_mean + u_mean + 1e-6) * 100
        
        print(f"{feat:<20} {c_mean:<15.2f} {u_mean:<15.2f} {sep:.1f}%")
    
    print(f"\n✅ Features extracted successfully!")
    print(f"Next step: Run 'python scripts/train_model.py' to train ML model")

if __name__ == "__main__":
    main()
