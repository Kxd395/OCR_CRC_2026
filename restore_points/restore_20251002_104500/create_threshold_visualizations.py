#!/usr/bin/env python3
"""
Create multi-threshold visualization showing what different thresholds would detect
"""
import cv2
import numpy as np
import json
from pathlib import Path

def analyze_checkbox(img_gray, x, y, w, h):
    """Extract and analyze a single checkbox"""
    checkbox = img_gray[y:y+h, x:x+w]
    _, binary = cv2.threshold(checkbox, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    fill_pct = (np.sum(binary == 255) / binary.size) * 100
    return fill_pct

def get_color_for_threshold(fill_pct):
    """Return color based on fill percentage thresholds"""
    if fill_pct >= 55:
        return (0, 0, 255), "CHECKED (≥55%)"  # Red - definitely checked
    elif fill_pct >= 40:
        return (0, 165, 255), "HIGH (40-54%)"  # Orange - likely checked
    elif fill_pct >= 30:
        return (0, 255, 255), "MEDIUM (30-39%)"  # Yellow - maybe marked
    elif fill_pct >= 20:
        return (0, 255, 0), "LOW (20-29%)"  # Green - light mark
    else:
        return (128, 128, 128), "EMPTY (<20%)"  # Gray - empty

def create_threshold_visualization(img_path, template, output_path):
    """Create visualization with color-coded thresholds"""
    img = cv2.imread(str(img_path))
    if img is None:
        return False, None
    
    h, w = img.shape[:2]
    overlay = img.copy()
    
    stats = {
        'checked_55': 0,
        'high_40': 0,
        'medium_30': 0,
        'low_20': 0,
        'empty': 0,
        'fills': []
    }
    
    # Analyze and draw all checkboxes
    for roi in template['checkbox_rois_norm']:
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        if x < 0 or y < 0 or x+roi_w > w or y+roi_h > h:
            continue
        
        # Get fill percentage
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        fill_pct = analyze_checkbox(img_gray, x, y, roi_w, roi_h)
        stats['fills'].append(fill_pct)
        
        # Get color based on threshold
        color, label = get_color_for_threshold(fill_pct)
        
        # Update stats
        if fill_pct >= 55:
            stats['checked_55'] += 1
        elif fill_pct >= 40:
            stats['high_40'] += 1
        elif fill_pct >= 30:
            stats['medium_30'] += 1
        elif fill_pct >= 20:
            stats['low_20'] += 1
        else:
            stats['empty'] += 1
        
        # Draw rectangle with appropriate color
        cv2.rectangle(overlay, (x, y), (x+roi_w, y+roi_h), color, 3)
        
        # Add fill percentage text
        text = f"{fill_pct:.0f}%"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        text_x = x + (roi_w - text_size[0]) // 2
        text_y = y + (roi_h + text_size[1]) // 2
        
        # Background for text
        cv2.rectangle(overlay, (text_x-2, text_y-text_size[1]-2), 
                     (text_x+text_size[0]+2, text_y+2), (255, 255, 255), -1)
        cv2.putText(overlay, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Add checkbox ID above
        cv2.putText(overlay, roi['id'], (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    # Create legend
    legend_height = 180
    legend = np.ones((legend_height, w, 3), dtype=np.uint8) * 255
    
    y_pos = 30
    legend_items = [
        ((0, 0, 255), f"■ CHECKED (≥55%): {stats['checked_55']} boxes"),
        ((0, 165, 255), f"■ HIGH (40-54%): {stats['high_40']} boxes"),
        ((0, 255, 255), f"■ MEDIUM (30-39%): {stats['medium_30']} boxes"),
        ((0, 255, 0), f"■ LOW (20-29%): {stats['low_20']} boxes"),
        ((128, 128, 128), f"■ EMPTY (<20%): {stats['empty']} boxes")
    ]
    
    cv2.putText(legend, "Threshold Detection Levels:", (20, 20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    for color, text in legend_items:
        cv2.rectangle(legend, (20, y_pos-15), (40, y_pos), color, -1)
        cv2.putText(legend, text, (50, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        y_pos += 30
    
    # Add statistics
    if stats['fills']:
        avg_fill = np.mean(stats['fills'])
        max_fill = np.max(stats['fills'])
        cv2.putText(legend, f"Average fill: {avg_fill:.1f}%  |  Max fill: {max_fill:.1f}%", 
                   (20, y_pos+10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Combine image and legend
    result = np.vstack([overlay, legend])
    
    cv2.imwrite(str(output_path), result)
    return True, stats

def main():
    run_dir = Path("artifacts/run_20251001_185300")
    
    # Load template
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    with open(template_path) as f:
        template = json.load(f)
    
    # Find aligned cropped images
    aligned_dir = run_dir / "02_step2_alignment_and_crop/aligned_cropped"
    image_files = sorted(aligned_dir.glob("page_*.png"))
    
    print(f"Creating threshold visualizations for {len(image_files)} pages...")
    print("\nColor Legend:")
    print("  🔴 RED (≥55%):    CHECKED - Current threshold")
    print("  🟠 ORANGE (40-54%): HIGH - Likely checked")
    print("  🟡 YELLOW (30-39%): MEDIUM - Possibly marked")
    print("  🟢 GREEN (20-29%):  LOW - Light mark or noise")
    print("  ⚪ GRAY (<20%):    EMPTY - No mark detected")
    print()
    
    # Create output directory
    output_dir = run_dir / "threshold_visualizations"
    output_dir.mkdir(exist_ok=True)
    
    # Process all pages
    total_stats = {
        'checked_55': 0,
        'high_40': 0,
        'medium_30': 0,
        'low_20': 0,
        'empty': 0
    }
    
    success_count = 0
    for img_path in image_files:
        page_num = img_path.stem.split('_')[1]
        output_path = output_dir / f"page_{page_num}_thresholds.png"
        
        print(f"Processing page {page_num}...", end=" ")
        success, stats = create_threshold_visualization(img_path, template, output_path)
        
        if success:
            print(f"✅ Saved - R:{stats['checked_55']} O:{stats['high_40']} "
                  f"Y:{stats['medium_30']} G:{stats['low_20']} Gray:{stats['empty']}")
            success_count += 1
            
            # Accumulate stats
            for key in total_stats:
                total_stats[key] += stats[key]
        else:
            print("❌ Failed")
    
    print("\n" + "="*70)
    print(f"✅ Successfully processed {success_count}/{len(image_files)} pages")
    print(f"📁 Visualizations saved to: {output_dir}")
    
    print("\n" + "="*70)
    print("OVERALL DETECTION BY THRESHOLD")
    print("="*70)
    total_boxes = sum(total_stats.values())
    print(f"Total checkboxes: {total_boxes}")
    print(f"\n🔴 CHECKED (≥55%):   {total_stats['checked_55']:3d} ({total_stats['checked_55']/total_boxes*100:.1f}%)")
    print(f"🟠 HIGH (40-54%):    {total_stats['high_40']:3d} ({total_stats['high_40']/total_boxes*100:.1f}%)")
    print(f"🟡 MEDIUM (30-39%):  {total_stats['medium_30']:3d} ({total_stats['medium_30']/total_boxes*100:.1f}%)")
    print(f"🟢 LOW (20-29%):     {total_stats['low_20']:3d} ({total_stats['low_20']/total_boxes*100:.1f}%)")
    print(f"⚪ EMPTY (<20%):     {total_stats['empty']:3d} ({total_stats['empty']/total_boxes*100:.1f}%)")
    
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)
    
    if total_stats['checked_55'] > 0:
        print(f"✅ {total_stats['checked_55']} boxes would be detected as CHECKED at 55% threshold")
    else:
        print("⚠️  No boxes meet the 55% threshold (current setting)")
    
    if total_stats['high_40'] > 0:
        print(f"💡 {total_stats['high_40']} boxes at 40-54% might be checked but below threshold")
    
    if total_stats['medium_30'] > 0:
        print(f"💡 {total_stats['medium_30']} boxes at 30-39% could be light marks")
    
    if total_stats['empty'] == total_boxes:
        print("\n✅ CONCLUSION: All forms appear blank (all boxes <20% fill)")
        print("   This is normal for empty survey forms.")
    
    print(f"\n📖 To view visualizations:")
    print(f"   open {output_dir}")
    print(f"\n📖 To view first page:")
    print(f"   open {output_dir}/page_0001_thresholds.png")

if __name__ == "__main__":
    main()
