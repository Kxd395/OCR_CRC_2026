#!/usr/bin/env python3
"""
Narrow down and visualize the first row of checkboxes (Q1_0 through Q1_4).

This script helps identify the exact pixel locations of the first row of 
checkboxes on the aligned and cropped image, allowing you to create an 
accurate grid definition.
"""

import cv2
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple


def load_template(template_path: Path) -> Dict:
    """Load template JSON with checkbox ROIs."""
    with open(template_path) as f:
        return json.load(f)


def denormalize_roi(roi: Dict, img_width: int, img_height: int) -> Dict:
    """Convert normalized coordinates to pixel coordinates."""
    return {
        'id': roi['id'],
        'x': int(roi['x'] * img_width),
        'y': int(roi['y'] * img_height),
        'w': int(roi['w'] * img_width),
        'h': int(roi['h'] * img_height)
    }


def draw_checkbox_roi(
    image: np.ndarray,
    roi: Dict,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """Draw a checkbox ROI on the image."""
    img = image.copy()
    
    # Draw rectangle
    cv2.rectangle(
        img,
        (roi['x'], roi['y']),
        (roi['x'] + roi['w'], roi['y'] + roi['h']),
        color,
        thickness
    )
    
    # Draw center point
    center_x = roi['x'] + roi['w'] // 2
    center_y = roi['y'] + roi['h'] // 2
    cv2.circle(img, (center_x, center_y), 3, (255, 0, 0), -1)
    
    # Add label
    label = roi['id']
    cv2.putText(
        img,
        label,
        (roi['x'], roi['y'] - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1
    )
    
    return img


def extract_first_row_checkboxes(template: Dict) -> List[Dict]:
    """Extract only Q1 checkboxes (first row)."""
    q1_checkboxes = []
    for roi in template.get('checkbox_rois_norm', []):
        if roi['id'].startswith('Q1_'):
            q1_checkboxes.append(roi)
    
    # Sort by column (x coordinate)
    q1_checkboxes.sort(key=lambda r: r['x'])
    return q1_checkboxes


def create_first_row_visualization(
    image_path: Path,
    template_path: Path,
    output_path: Path
) -> Dict:
    """
    Create visualization of first row checkboxes with measurements.
    
    Returns:
        Dictionary with pixel coordinates and measurements
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    
    img_height, img_width = img.shape[:2]
    print(f"Image dimensions: {img_width}x{img_height}")
    
    # Load template
    template = load_template(template_path)
    
    # Get Q1 checkboxes
    q1_rois_norm = extract_first_row_checkboxes(template)
    print(f"\nFound {len(q1_rois_norm)} Q1 checkboxes")
    
    # Convert to pixel coordinates
    q1_rois_px = [denormalize_roi(roi, img_width, img_height) for roi in q1_rois_norm]
    
    # Create visualization
    vis_img = img.copy()
    
    # Draw each checkbox
    colors = [
        (0, 255, 0),    # Green - Q1_0
        (0, 255, 255),  # Yellow - Q1_1
        (255, 0, 0),    # Blue - Q1_2
        (255, 0, 255),  # Magenta - Q1_3
        (255, 255, 0),  # Cyan - Q1_4
    ]
    
    for i, roi in enumerate(q1_rois_px):
        color = colors[i % len(colors)]
        vis_img = draw_checkbox_roi(vis_img, roi, color, thickness=3)
    
    # Draw horizontal line through centers
    if q1_rois_px:
        first_roi = q1_rois_px[0]
        last_roi = q1_rois_px[-1]
        
        y_center = first_roi['y'] + first_roi['h'] // 2
        
        cv2.line(
            vis_img,
            (0, y_center),
            (img_width, y_center),
            (0, 0, 255),  # Red
            1
        )
        
        # Draw vertical lines at left and right edges
        left_x = first_roi['x']
        right_x = last_roi['x'] + last_roi['w']
        
        cv2.line(vis_img, (left_x, 0), (left_x, img_height), (0, 0, 255), 1)
        cv2.line(vis_img, (right_x, 0), (right_x, img_height), (0, 0, 255), 1)
    
    # Add measurements overlay
    overlay = vis_img.copy()
    cv2.rectangle(overlay, (10, 10), (500, 250), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, vis_img, 0.3, 0, vis_img)
    
    # Add text measurements
    y_offset = 35
    cv2.putText(vis_img, "First Row (Q1) Measurements:", (20, y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    y_offset += 25
    
    cv2.putText(vis_img, f"Image: {img_width}x{img_height}px", (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    y_offset += 20
    
    if q1_rois_px:
        # Calculate spacing
        spacings = []
        for i in range(len(q1_rois_px) - 1):
            spacing = q1_rois_px[i+1]['x'] - (q1_rois_px[i]['x'] + q1_rois_px[i]['w'])
            spacings.append(spacing)
        
        avg_spacing = sum(spacings) / len(spacings) if spacings else 0
        
        cv2.putText(vis_img, f"Num checkboxes: {len(q1_rois_px)}", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        cv2.putText(vis_img, f"Row Y center: {y_center}px", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        cv2.putText(vis_img, f"Box width: {q1_rois_px[0]['w']}px", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        cv2.putText(vis_img, f"Box height: {q1_rois_px[0]['h']}px", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        cv2.putText(vis_img, f"Avg spacing: {avg_spacing:.1f}px", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        cv2.putText(vis_img, f"Left edge: {left_x}px", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 20
        
        cv2.putText(vis_img, f"Right edge: {right_x}px", (20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Save visualization
    cv2.imwrite(str(output_path), vis_img)
    print(f"\n✅ Saved visualization to: {output_path}")
    
    # Create zoomed view of first row
    if q1_rois_px:
        # Crop to first row with padding
        top = max(0, first_roi['y'] - 50)
        bottom = min(img_height, first_roi['y'] + first_roi['h'] + 50)
        left = max(0, first_roi['x'] - 50)
        right = min(img_width, last_roi['x'] + last_roi['w'] + 50)
        
        cropped = vis_img[top:bottom, left:right]
        zoomed_path = output_path.parent / f"{output_path.stem}_zoomed.png"
        cv2.imwrite(str(zoomed_path), cropped)
        print(f"✅ Saved zoomed view to: {zoomed_path}")
    
    # Prepare measurements dictionary
    measurements = {
        "image_dimensions": {
            "width": img_width,
            "height": img_height
        },
        "first_row_checkboxes": []
    }
    
    for i, (roi_norm, roi_px) in enumerate(zip(q1_rois_norm, q1_rois_px)):
        measurements["first_row_checkboxes"].append({
            "id": roi_px['id'],
            "index": i,
            "normalized": {
                "x": roi_norm['x'],
                "y": roi_norm['y'],
                "w": roi_norm['w'],
                "h": roi_norm['h']
            },
            "pixels": {
                "x": roi_px['x'],
                "y": roi_px['y'],
                "w": roi_px['w'],
                "h": roi_px['h'],
                "center_x": roi_px['x'] + roi_px['w'] // 2,
                "center_y": roi_px['y'] + roi_px['h'] // 2
            }
        })
    
    if spacings:
        measurements["spacing"] = {
            "between_boxes_px": spacings,
            "average_px": avg_spacing,
            "std_dev_px": float(np.std(spacings))
        }
    
    # Save measurements JSON
    json_path = output_path.parent / f"{output_path.stem}_measurements.json"
    with open(json_path, 'w') as f:
        json.dump(measurements, f, indent=2)
    print(f"✅ Saved measurements to: {json_path}")
    
    return measurements


def print_summary(measurements: Dict) -> None:
    """Print a summary of measurements."""
    print("\n" + "="*60)
    print("FIRST ROW CHECKBOX GRID SUMMARY")
    print("="*60)
    
    img_dims = measurements['image_dimensions']
    print(f"\nImage: {img_dims['width']}x{img_dims['height']}px")
    
    checkboxes = measurements['first_row_checkboxes']
    print(f"\nCheckboxes in first row: {len(checkboxes)}")
    
    if checkboxes:
        first = checkboxes[0]
        last = checkboxes[-1]
        
        print(f"\nFirst checkbox (Q1_0):")
        print(f"  Normalized: ({first['normalized']['x']:.3f}, {first['normalized']['y']:.3f})")
        print(f"  Pixels:     ({first['pixels']['x']}, {first['pixels']['y']})")
        print(f"  Size:       {first['pixels']['w']}x{first['pixels']['h']}px")
        
        print(f"\nLast checkbox (Q1_4):")
        print(f"  Normalized: ({last['normalized']['x']:.3f}, {last['normalized']['y']:.3f})")
        print(f"  Pixels:     ({last['pixels']['x']}, {last['pixels']['y']})")
        
        if 'spacing' in measurements:
            spacing = measurements['spacing']
            print(f"\nSpacing between boxes:")
            print(f"  Average: {spacing['average_px']:.1f}px")
            print(f"  Std dev: {spacing['std_dev_px']:.1f}px")
            print(f"  Individual spacings: {[f'{s:.1f}' for s in spacing['between_boxes_px']]}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    import sys
    
    # Paths
    project_root = Path(__file__).parent.parent
    run_dir = project_root / "artifacts/run_20251001_185300"
    
    image_path = run_dir / "02_step2_alignment_and_crop/aligned_cropped/page_0001_aligned_cropped.png"
    template_path = project_root / "templates/crc_survey_l_anchors_v1/template.json"
    output_path = run_dir / "first_row_grid_visualization.png"
    
    # Check if image exists
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)
    
    print("Analyzing first row checkboxes...")
    print(f"Image: {image_path}")
    print(f"Template: {template_path}")
    
    # Create visualization
    measurements = create_first_row_visualization(
        image_path,
        template_path,
        output_path
    )
    
    # Print summary
    print_summary(measurements)
    
    print(f"\n✅ Done! Open the visualization to review:")
    print(f"   {output_path}")
    print(f"   {output_path.parent / f'{output_path.stem}_zoomed.png'}")
