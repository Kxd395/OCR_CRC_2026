#!/usr/bin/env python3
"""
Comprehensive analysis script showing:
1. Anchor detection and positioning
2. Alignment quality with residuals
3. Checkbox identification and fill scores
4. Accuracy ranking
"""
import json, pathlib, sys
from collections import defaultdict

def main():
    run_dir = pathlib.Path("artifacts/20251001_175110")
    
    print("=" * 80)
    print(" COMPREHENSIVE OCR ANALYSIS REPORT")
    print("=" * 80)
    
    # 1. ANCHOR DETECTION
    print("\n🎯 STEP 1: ANCHOR DETECTION (L-marks)")
    print("-" * 80)
    tpl = json.load(open("templates/crc_survey_l_anchors_v1/template.json"))
    anchors = tpl['anchors_norm']
    print(f"Template expects {len(anchors)} anchor points at corners:")
    for i, a in enumerate(anchors, 1):
        corner = ["Top-Left", "Top-Right", "Bottom-Right", "Bottom-Left"][i-1]
        print(f"  Anchor {i} ({corner:12s}): x={a['x']:.1%}, y={a['y']:.1%}")
    
    # 2. ALIGNMENT QUALITY
    print("\n📐 STEP 2: PAGE ALIGNMENT (Homography)")
    print("-" * 80)
    homo_file = run_dir / "logs/homography.json"
    if not homo_file.exists():
        print("❌ No homography data found - alignment not completed")
        return
        
    homo = json.load(open(homo_file))
    print(f"Pages processed: {len(homo['pages'])}")
    print(f"Thresholds: OK ≤ {homo['thresholds']['warn_px']}px, "
          f"WARN ≤ {homo['thresholds']['fail_px']}px")
    
    # Quality summary
    quality_counts = defaultdict(int)
    residuals = []
    for page_data in homo['pages'].values():
        quality_counts[page_data.get('quality', 'unknown')] += 1
        residuals.append(page_data.get('residual_px', 0))
    
    print(f"\nAlignment Quality:")
    print(f"  ✅ OK:   {quality_counts['ok']} pages")
    print(f"  ⚠️  WARN: {quality_counts['warn']} pages")
    print(f"  ❌ FAIL: {quality_counts['fail']} pages")
    
    if residuals:
        print(f"\nResidual Statistics:")
        print(f"  Average: {sum(residuals)/len(residuals):.3f} px")
        print(f"  Range: {min(residuals):.3f} - {max(residuals):.3f} px")
    
    # 3. CHECKBOX DETECTION
    print("\n☑️  STEP 3: CHECKBOX IDENTIFICATION")
    print("-" * 80)
    checkboxes = tpl.get('checkbox_rois_norm', [])
    print(f"Template defines {len(checkboxes)} checkbox ROIs")
    
    # Group by question
    questions = defaultdict(list)
    for cb in checkboxes:
        q_id = cb['id'].rsplit('_', 1)[0]  # e.g., "Q1" from "Q1_0"
        questions[q_id].append(cb)
    
    print(f"Questions with checkboxes: {len(questions)}")
    for q_id in sorted(questions.keys())[:5]:
        print(f"  {q_id}: {len(questions[q_id])} options")
    
    # 4. OCR RESULTS & ACCURACY
    print("\n📊 STEP 4: OCR RESULTS & ACCURACY")
    print("-" * 80)
    
    ocr_results = run_dir / "logs/ocr_results.json"
    if not ocr_results.exists():
        print("⏳ OCR extraction not yet completed")
        print("   Run: make ocr")
        return
    
    results = json.load(open(ocr_results))
    print(f"Pages with OCR results: {len(results.get('pages', {}))}")
    
    # Analyze checkbox scores
    all_scores = []
    marked_count = 0
    unmarked_count = 0
    threshold = 0.55
    
    for page_name, page_data in results.get('pages', {}).items():
        for cb_id, score in page_data.get('checkboxes', {}).items():
            all_scores.append((cb_id, score, score >= threshold))
            if score >= threshold:
                marked_count += 1
            else:
                unmarked_count += 1
    
    if all_scores:
        print(f"\nCheckbox Detection Summary:")
        print(f"  Total checkboxes analyzed: {len(all_scores)}")
        print(f"  Marked (≥{threshold}): {marked_count}")
        print(f"  Unmarked (<{threshold}): {unmarked_count}")
        print(f"  Fill threshold: {threshold * 100}%")
        
        # Top marked checkboxes
        marked = sorted([s for s in all_scores if s[2]], key=lambda x: x[1], reverse=True)
        if marked:
            print(f"\n  Top 10 highest fill scores:")
            for cb_id, score, _ in marked[:10]:
                print(f"    {cb_id}: {score:.1%} ✓")
    
    # 5. OVERALL ACCURACY RANKING
    print("\n🏆 STEP 5: ACCURACY RANKING")
    print("-" * 80)
    
    # Calculate confidence score
    good_alignment = quality_counts['ok']
    total_pages = len(homo['pages'])
    alignment_score = (good_alignment / total_pages * 100) if total_pages > 0 else 0
    
    avg_residual = sum(residuals) / len(residuals) if residuals else 0
    residual_score = max(0, 100 - (avg_residual / homo['thresholds']['warn_px'] * 100))
    
    overall_score = (alignment_score + residual_score) / 2
    
    print(f"Alignment Accuracy: {alignment_score:.1f}% ({good_alignment}/{total_pages} pages OK)")
    print(f"Residual Quality: {residual_score:.1f}% (avg {avg_residual:.3f}px)")
    print(f"\n🎯 OVERALL ACCURACY: {overall_score:.1f}%")
    
    if overall_score >= 95:
        print("   Rating: ⭐⭐⭐⭐⭐ EXCELLENT")
    elif overall_score >= 85:
        print("   Rating: ⭐⭐⭐⭐ VERY GOOD")
    elif overall_score >= 75:
        print("   Rating: ⭐⭐⭐ GOOD")
    else:
        print("   Rating: ⭐⭐ NEEDS IMPROVEMENT")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
