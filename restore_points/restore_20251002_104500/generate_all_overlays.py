#!/usr/bin/env python3
"""
Master script to create all visualizations for a run in organized folders
"""
import cv2
import numpy as np
import json
import sys
from pathlib import Path
from datetime import datetime

def analyze_checkbox(img_gray, x, y, w, h):
    """Extract and analyze a single checkbox"""
    checkbox = img_gray[y:y+h, x:x+w]
    _, binary = cv2.threshold(checkbox, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    fill_pct = (np.sum(binary == 255) / binary.size) * 100
    return fill_pct

def get_color_for_threshold(fill_pct):
    """Return color based on fill percentage thresholds"""
    if fill_pct >= 55:
        return (0, 0, 255), "CHECKED"  # Red
    elif fill_pct >= 40:
        return (0, 165, 255), "HIGH"  # Orange
    elif fill_pct >= 30:
        return (0, 255, 255), "MEDIUM"  # Yellow
    elif fill_pct >= 20:
        return (0, 255, 0), "LOW"  # Green
    else:
        return (128, 128, 128), "EMPTY"  # Gray

def create_basic_overlay(img_path, template, output_path):
    """Create basic overlay with green boxes"""
    img = cv2.imread(str(img_path))
    if img is None:
        return False
    
    h, w = img.shape[:2]
    overlay = img.copy()
    
    for roi in template['checkbox_rois_norm']:
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        cv2.rectangle(overlay, (x, y), (x+roi_w, y+roi_h), (0, 255, 0), 2)
        cv2.putText(overlay, roi['id'], (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imwrite(str(output_path), overlay)
    return True

def create_threshold_overlay(img_path, template, output_path):
    """Create threshold overlay with color-coded fill levels"""
    img = cv2.imread(str(img_path))
    if img is None:
        return False, None
    
    h, w = img.shape[:2]
    overlay = img.copy()
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    stats = {
        'checked_55': 0,
        'high_40': 0,
        'medium_30': 0,
        'low_20': 0,
        'empty': 0,
        'fills': []
    }
    
    for roi in template['checkbox_rois_norm']:
        x = int(roi['x'] * w)
        y = int(roi['y'] * h)
        roi_w = int(roi['w'] * w)
        roi_h = int(roi['h'] * h)
        
        if x < 0 or y < 0 or x+roi_w > w or y+roi_h > h:
            continue
        
        fill_pct = analyze_checkbox(img_gray, x, y, roi_w, roi_h)
        stats['fills'].append(fill_pct)
        
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
        
        # Draw rectangle
        cv2.rectangle(overlay, (x, y), (x+roi_w, y+roi_h), color, 3)
        
        # Add fill percentage
        text = f"{fill_pct:.0f}%"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
        text_x = x + (roi_w - text_size[0]) // 2
        text_y = y + (roi_h + text_size[1]) // 2
        
        cv2.rectangle(overlay, (text_x-2, text_y-text_size[1]-2), 
                     (text_x+text_size[0]+2, text_y+2), (255, 255, 255), -1)
        cv2.putText(overlay, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Add checkbox ID
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
    
    if stats['fills']:
        avg_fill = np.mean(stats['fills'])
        max_fill = np.max(stats['fills'])
        cv2.putText(legend, f"Average: {avg_fill:.1f}%  |  Max: {max_fill:.1f}%", 
                   (20, y_pos+10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    result = np.vstack([overlay, legend])
    cv2.imwrite(str(output_path), result)
    
    return True, stats

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_all_overlays.py <run_directory>")
        sys.exit(1)
    
    run_dir = Path(sys.argv[1])
    
    print("="*70)
    print(f"GENERATING OVERLAYS FOR: {run_dir.name}")
    print("="*70)
    
    # Load template
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)
    
    with open(template_path) as f:
        template = json.load(f)
    
    # Find aligned cropped images
    aligned_dir = run_dir / "02_step2_alignment_and_crop/aligned_cropped"
    if not aligned_dir.exists():
        print(f"Error: Aligned images not found at {aligned_dir}")
        sys.exit(1)
    
    image_files = sorted(aligned_dir.glob("page_*.png"))
    if not image_files:
        print(f"Error: No images found in {aligned_dir}")
        sys.exit(1)
    
    print(f"Found {len(image_files)} pages to process")
    
    # Create main overlays directory
    overlays_dir = run_dir / "overlays"
    overlays_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    basic_dir = overlays_dir / "basic"
    threshold_dir = overlays_dir / "threshold"
    basic_dir.mkdir(exist_ok=True)
    threshold_dir.mkdir(exist_ok=True)
    
    print(f"\nOutput directories:")
    print(f"  📁 {basic_dir}")
    print(f"  📁 {threshold_dir}")
    
    # Process all pages
    print("\n" + "="*70)
    print("PROCESSING PAGES")
    print("="*70)
    
    total_stats = {
        'checked_55': 0,
        'high_40': 0,
        'medium_30': 0,
        'low_20': 0,
        'empty': 0
    }
    
    for img_path in image_files:
        page_num = img_path.stem.split('_')[1]
        
        # Create basic overlay
        basic_output = basic_dir / f"page_{page_num}_basic.png"
        basic_success = create_basic_overlay(img_path, template, basic_output)
        
        # Create threshold overlay
        threshold_output = threshold_dir / f"page_{page_num}_threshold.png"
        threshold_success, stats = create_threshold_overlay(img_path, template, threshold_output)
        
        status = "✅" if (basic_success and threshold_success) else "❌"
        
        if threshold_success and stats:
            print(f"{status} Page {page_num}: "
                  f"R:{stats['checked_55']} O:{stats['high_40']} "
                  f"Y:{stats['medium_30']} G:{stats['low_20']} Gray:{stats['empty']}")
            
            for key in total_stats:
                total_stats[key] += stats[key]
    
    # Generate summary report
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    
    total_boxes = sum(total_stats.values())
    
    print(f"\nTotal pages: {len(image_files)}")
    print(f"Total checkboxes: {total_boxes}")
    print(f"\nDetection by threshold:")
    print(f"  🔴 CHECKED (≥55%):   {total_stats['checked_55']:3d} ({total_stats['checked_55']/total_boxes*100:5.1f}%)")
    print(f"  🟠 HIGH (40-54%):    {total_stats['high_40']:3d} ({total_stats['high_40']/total_boxes*100:5.1f}%)")
    print(f"  🟡 MEDIUM (30-39%):  {total_stats['medium_30']:3d} ({total_stats['medium_30']/total_boxes*100:5.1f}%)")
    print(f"  🟢 LOW (20-29%):     {total_stats['low_20']:3d} ({total_stats['low_20']/total_boxes*100:5.1f}%)")
    print(f"  ⚪ EMPTY (<20%):     {total_stats['empty']:3d} ({total_stats['empty']/total_boxes*100:5.1f}%)")
    
    # Save summary to file
    summary_path = overlays_dir / "SUMMARY.txt"
    with open(summary_path, 'w') as f:
        f.write(f"Overlay Generation Summary\n")
        f.write(f"{'='*70}\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Run: {run_dir.name}\n")
        f.write(f"Pages processed: {len(image_files)}\n")
        f.write(f"Total checkboxes: {total_boxes}\n\n")
        f.write(f"Detection Results:\n")
        f.write(f"  CHECKED (≥55%):   {total_stats['checked_55']:3d} ({total_stats['checked_55']/total_boxes*100:5.1f}%)\n")
        f.write(f"  HIGH (40-54%):    {total_stats['high_40']:3d} ({total_stats['high_40']/total_boxes*100:5.1f}%)\n")
        f.write(f"  MEDIUM (30-39%):  {total_stats['medium_30']:3d} ({total_stats['medium_30']/total_boxes*100:5.1f}%)\n")
        f.write(f"  LOW (20-29%):     {total_stats['low_20']:3d} ({total_stats['low_20']/total_boxes*100:5.1f}%)\n")
        f.write(f"  EMPTY (<20%):     {total_stats['empty']:3d} ({total_stats['empty']/total_boxes*100:5.1f}%)\n\n")
        f.write(f"Output Directories:\n")
        f.write(f"  Basic overlays: overlays/basic/\n")
        f.write(f"  Threshold overlays: overlays/threshold/\n")
    
    print(f"\n✅ Summary saved to: {summary_path}")
    
    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)
    print(f"\n📁 View overlays:")
    print(f"   open {overlays_dir}")
    print(f"\n📁 View basic overlays (green boxes):")
    print(f"   open {basic_dir}")
    print(f"\n📁 View threshold overlays (color-coded):")
    print(f"   open {threshold_dir}")
    print(f"\n📄 View summary:")
    print(f"   cat {summary_path}")

if __name__ == "__main__":
    main()
