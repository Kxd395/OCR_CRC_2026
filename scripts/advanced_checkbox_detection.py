#!/usr/bin/env python3
"""
Advanced checkbox detection using multiple methods
"""
import cv2
import numpy as np
import json
from pathlib import Path
import sys

def method_1_otsu(checkbox):
    """Current method: Otsu thresholding"""
    _, binary = cv2.threshold(checkbox, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    fill_pct = (np.sum(binary == 255) / binary.size) * 100
    return fill_pct, binary

def method_2_adaptive(checkbox):
    """Adaptive thresholding - better for varying lighting"""
    binary = cv2.adaptiveThreshold(checkbox, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    fill_pct = (np.sum(binary == 255) / binary.size) * 100
    return fill_pct, binary

def method_3_mean_based(checkbox):
    """Mean intensity based detection"""
    mean_val = np.mean(checkbox)
    # Darker = more filled. Empty boxes ~200-240, filled boxes ~50-150
    # Invert the scale: higher fill% = darker
    fill_pct = ((255 - mean_val) / 255) * 100
    return fill_pct, None

def method_4_variance(checkbox):
    """Variance-based: filled boxes have more variation"""
    std_val = np.std(checkbox)
    # Higher std = more variation = likely filled
    # Normalize to 0-100 scale
    fill_pct = min((std_val / 80) * 100, 100)
    return fill_pct, None

def method_5_edge_detection(checkbox):
    """Edge detection - checkmarks have lots of edges"""
    edges = cv2.Canny(checkbox, 50, 150)
    fill_pct = (np.sum(edges > 0) / edges.size) * 100
    return fill_pct, edges

def analyze_checkbox_all_methods(img_gray, x, y, w, h):
    """Analyze checkbox with all methods"""
    checkbox = img_gray[y:y+h, x:x+w]
    
    results = {}
    results['otsu'], _ = method_1_otsu(checkbox)
    results['adaptive'], _ = method_2_adaptive(checkbox)
    results['mean'], _ = method_3_mean_based(checkbox)
    results['variance'], _ = method_4_variance(checkbox)
    results['edges'], _ = method_5_edge_detection(checkbox)
    
    # Calculate average
    results['average'] = np.mean(list(results.values()))
    
    return results, checkbox

def create_diagnostic_image(checkbox, results, roi_id):
    """Create a diagnostic image showing all methods"""
    h, w = checkbox.shape
    
    # Create grid: 3 rows x 3 cols
    cell_h, cell_w = h + 60, w + 60
    canvas = np.ones((cell_h * 3, cell_w * 3, 3), dtype=np.uint8) * 255
    
    # Method images
    _, otsu_bin = method_1_otsu(checkbox)
    _, adaptive_bin = method_2_adaptive(checkbox)
    _, edges_bin = method_5_edge_detection(checkbox)
    
    images = [
        ("Original", cv2.cvtColor(checkbox, cv2.COLOR_GRAY2BGR)),
        ("Otsu", cv2.cvtColor(otsu_bin, cv2.COLOR_GRAY2BGR)),
        ("Adaptive", cv2.cvtColor(adaptive_bin, cv2.COLOR_GRAY2BGR)),
        ("Edges", cv2.cvtColor(edges_bin, cv2.COLOR_GRAY2BGR)),
    ]
    
    # Place images
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for (title, img), (row, col) in zip(images, positions):
        y_start = row * cell_h + 30
        x_start = col * cell_w + 30
        canvas[y_start:y_start+h, x_start:x_start+w] = img
        
        # Add title
        cv2.putText(canvas, title, (x_start, y_start-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Add results text
    y_text = 2 * cell_h + 20
    texts = [
        f"{roi_id}",
        f"Otsu: {results['otsu']:.1f}%",
        f"Adaptive: {results['adaptive']:.1f}%",
        f"Mean: {results['mean']:.1f}%",
        f"Variance: {results['variance']:.1f}%",
        f"Edges: {results['edges']:.1f}%",
        f"AVERAGE: {results['average']:.1f}%",
    ]
    
    for i, text in enumerate(texts):
        y_pos = y_text + i * 25
        color = (0, 0, 255) if i == len(texts)-1 else (0, 0, 0)
        thickness = 2 if i == len(texts)-1 else 1
        cv2.putText(canvas, text, (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)
    
    return canvas

def main():
    if len(sys.argv) < 2:
        print("Usage: python advanced_checkbox_detection.py <run_directory> [page_num]")
        sys.exit(1)
    
    run_dir = Path(sys.argv[1])
    page_num = sys.argv[2] if len(sys.argv) > 2 else "0001"
    
    print("="*70)
    print("ADVANCED CHECKBOX DETECTION - MULTI-METHOD ANALYSIS")
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
    
    print(f"\nAnalyzing page {page_num}")
    print(f"Image: {w}×{h}")
    
    # Create output directory
    output_dir = run_dir / "advanced_detection"
    output_dir.mkdir(exist_ok=True)
    
    # Analyze all checkboxes
    print(f"\nMethod Comparison:")
    print("="*70)
    print(f"{'ID':<8} {'Otsu':<8} {'Adapt':<8} {'Mean':<8} {'Var':<8} {'Edge':<8} {'AVG':<8}")
    print("="*70)
    
    all_results = []
    
    for roi in template['checkbox_rois_norm']:
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        if x < 0 or y < 0 or x+roi_w > w or y+roi_h > h:
            continue
        
        results, checkbox = analyze_checkbox_all_methods(img_gray, x, y, roi_w, roi_h)
        results['id'] = roi['id']
        all_results.append(results)
        
        # Print results
        print(f"{roi['id']:<8} "
              f"{results['otsu']:<8.1f} "
              f"{results['adaptive']:<8.1f} "
              f"{results['mean']:<8.1f} "
              f"{results['variance']:<8.1f} "
              f"{results['edges']:<8.1f} "
              f"{results['average']:<8.1f}")
        
        # Save diagnostic image
        diagnostic = create_diagnostic_image(checkbox, results, roi['id'])
        diagnostic_path = output_dir / f"page_{page_num}_{roi['id']}_diagnostic.png"
        cv2.imwrite(str(diagnostic_path), diagnostic)
    
    print("="*70)
    
    # Analyze which method works best
    print("\n" + "="*70)
    print("METHOD ANALYSIS")
    print("="*70)
    
    methods = ['otsu', 'adaptive', 'mean', 'variance', 'edges', 'average']
    
    for method in methods:
        values = [r[method] for r in all_results]
        mean_val = np.mean(values)
        std_val = np.std(values)
        min_val = np.min(values)
        max_val = np.max(values)
        range_val = max_val - min_val
        
        print(f"\n{method.upper()}:")
        print(f"  Mean: {mean_val:.1f}%")
        print(f"  Std:  {std_val:.1f}%")
        print(f"  Range: {min_val:.1f}% - {max_val:.1f}% (span: {range_val:.1f}%)")
        
        # Count above 55% threshold
        above_55 = sum(1 for v in values if v >= 55)
        print(f"  Above 55%: {above_55}/{len(values)} ({above_55/len(values)*100:.1f}%)")
    
    # Save detailed results
    results_path = output_dir / f"page_{page_num}_analysis.json"
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ Analysis complete!")
    print(f"📁 Diagnostic images: {output_dir}")
    print(f"📄 Detailed results: {results_path}")
    print(f"\nTo view diagnostics:")
    print(f"  open {output_dir}")
    
    # Recommendation
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS")
    print("="*70)
    
    # Find method with best separation
    best_method = None
    best_range = 0
    
    for method in methods:
        values = [r[method] for r in all_results]
        range_val = np.max(values) - np.min(values)
        if range_val > best_range:
            best_range = range_val
            best_method = method
    
    print(f"\n✅ Best method: {best_method.upper()}")
    print(f"   (Largest range = {best_range:.1f}% = best separation)")
    print(f"\n💡 Review diagnostic images to see which method")
    print(f"   clearly shows the difference between filled/empty boxes")

if __name__ == "__main__":
    main()
