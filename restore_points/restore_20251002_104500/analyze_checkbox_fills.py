#!/usr/bin/env python3
"""
Analyze checkbox fill percentages across all pages to find checked boxes
"""
import cv2
import numpy as np
import json
from pathlib import Path
from collections import defaultdict

def analyze_checkbox(img_gray, x, y, w, h):
    """Extract and analyze a single checkbox"""
    checkbox = img_gray[y:y+h, x:x+w]
    _, binary = cv2.threshold(checkbox, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    fill_pct = (np.sum(binary == 255) / binary.size) * 100
    return fill_pct, checkbox

def main():
    run_dir = Path("artifacts/run_20251001_185300")
    
    # Load template
    with open("templates/crc_survey_l_anchors_v1/template.json") as f:
        template = json.load(f)
    
    # Find all aligned cropped images
    aligned_dir = run_dir / "02_step2_alignment_and_crop/aligned_cropped"
    image_files = sorted(aligned_dir.glob("page_*.png"))
    
    print(f"Analyzing {len(image_files)} pages for checkbox fill percentages...\n")
    
    # Track statistics
    all_fills = []
    page_stats = []
    highest_fills = []  # Track top filled checkboxes
    
    for img_path in image_files[:5]:  # Sample first 5 pages
        page_num = img_path.stem.split('_')[1]
        
        img = cv2.imread(str(img_path))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = img_gray.shape
        
        page_fills = []
        
        for roi in template['checkbox_rois_norm']:
            x = int(roi['x'] * w)
            y = int(roi['y'] * h)
            roi_w = int(roi['w'] * w)
            roi_h = int(roi['h'] * h)
            
            if x < 0 or y < 0 or x+roi_w > w or y+roi_h > h:
                continue
            
            fill_pct, _ = analyze_checkbox(img_gray, x, y, roi_w, roi_h)
            page_fills.append(fill_pct)
            all_fills.append(fill_pct)
            
            # Track high-fill checkboxes
            if fill_pct > 20:  # Above normal empty box range
                highest_fills.append({
                    'page': page_num,
                    'checkbox': roi['id'],
                    'fill': fill_pct
                })
        
        avg_fill = np.mean(page_fills)
        max_fill = np.max(page_fills)
        min_fill = np.min(page_fills)
        
        page_stats.append({
            'page': page_num,
            'avg': avg_fill,
            'max': max_fill,
            'min': min_fill,
            'count_over_20': sum(1 for f in page_fills if f > 20),
            'count_over_30': sum(1 for f in page_fills if f > 30),
            'count_over_55': sum(1 for f in page_fills if f >= 55)
        })
        
        print(f"Page {page_num}: avg={avg_fill:.1f}%, max={max_fill:.1f}%, "
              f"min={min_fill:.1f}%, >20%: {page_stats[-1]['count_over_20']}, "
              f">55%: {page_stats[-1]['count_over_55']}")
    
    print("\n" + "="*70)
    print("OVERALL STATISTICS")
    print("="*70)
    
    overall_avg = np.mean(all_fills)
    overall_max = np.max(all_fills)
    overall_min = np.min(all_fills)
    overall_std = np.std(all_fills)
    
    print(f"Total checkboxes analyzed: {len(all_fills)}")
    print(f"Average fill: {overall_avg:.1f}%")
    print(f"Max fill: {overall_max:.1f}%")
    print(f"Min fill: {overall_min:.1f}%")
    print(f"Std deviation: {overall_std:.1f}%")
    
    # Count by threshold
    over_15 = sum(1 for f in all_fills if f >= 15)
    over_20 = sum(1 for f in all_fills if f >= 20)
    over_30 = sum(1 for f in all_fills if f >= 30)
    over_40 = sum(1 for f in all_fills if f >= 40)
    over_55 = sum(1 for f in all_fills if f >= 55)
    
    print(f"\nCheckboxes by fill threshold:")
    print(f"  ≥15%: {over_15} ({over_15/len(all_fills)*100:.1f}%)")
    print(f"  ≥20%: {over_20} ({over_20/len(all_fills)*100:.1f}%)")
    print(f"  ≥30%: {over_30} ({over_30/len(all_fills)*100:.1f}%)")
    print(f"  ≥40%: {over_40} ({over_40/len(all_fills)*100:.1f}%)")
    print(f"  ≥55%: {over_55} ({over_55/len(all_fills)*100:.1f}%) ← Current threshold")
    
    if highest_fills:
        print(f"\n" + "="*70)
        print("HIGHEST FILL PERCENTAGES (>20%)")
        print("="*70)
        highest_fills.sort(key=lambda x: x['fill'], reverse=True)
        for item in highest_fills[:20]:  # Top 20
            print(f"Page {item['page']}, {item['checkbox']}: {item['fill']:.1f}%")
    
    print(f"\n" + "="*70)
    print("ANALYSIS")
    print("="*70)
    
    if over_55 == 0:
        print("⚠️  NO CHECKBOXES detected as checked (≥55% threshold)")
        print("\nPossible reasons:")
        print("1. ✅ Forms are genuinely blank (no filled checkboxes)")
        print("2. ⚠️  Threshold too high (55% may need adjustment)")
        print("3. ⚠️  ROI alignment slightly off (not capturing checkbox marks)")
        
        if over_20 > 0:
            print(f"\n💡 SUGGESTION: {over_20} checkboxes have >20% fill.")
            print("   These might be filled but detected as 'empty'.")
            print("   Consider lowering threshold to 20-30% or visually inspect these.")
        else:
            print("\n💡 CONCLUSION: Forms appear genuinely blank (all <20% fill).")
    else:
        print(f"✅ {over_55} checkboxes detected as CHECKED (≥55% fill)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
