#!/usr/bin/env python3
"""
STEP 1: Find L-shaped anchor marks on each page
- Detects corner anchors using contour analysis
- Saves detailed detection logs
- Creates visualization showing detected anchors
"""
import argparse, json, pathlib, time
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

def find_l_marks(gray_img, approx_xy, search_window=80):
    """
    Find L-shaped anchor marks near expected position.
    Returns: (x, y, confidence) or None if not found
    """
    h, w = gray_img.shape[:2]
    ax, ay = int(approx_xy[0]), int(approx_xy[1])
    
    # Define search region
    x0 = max(0, ax - search_window)
    x1 = min(w, ax + search_window)
    y0 = max(0, ay - search_window)
    y1 = min(h, ay + search_window)
    
    roi = gray_img[y0:y1, x0:x1]
    if roi.size == 0:
        return None
    
    # Binarize
    blur = cv2.GaussianBlur(roi, (5, 5), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Find largest contour (likely the L-mark)
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    
    if area < 10:  # Too small
        return None
    
    # Calculate centroid
    M = cv2.moments(largest)
    if M["m00"] == 0:
        cx, cy = largest.reshape(-1, 2).mean(axis=0)
    else:
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
    
    # Convert back to full image coordinates
    abs_x = x0 + cx
    abs_y = y0 + cy
    
    # Calculate confidence based on area and shape
    perimeter = cv2.arcLength(largest, True)
    if perimeter == 0:
        confidence = 0.0
    else:
        # L-shapes have high perimeter-to-area ratio
        compactness = 4 * np.pi * area / (perimeter * perimeter)
        confidence = min(1.0, area / 500) * (1.0 - compactness)  # L-marks are not compact
    
    return {
        'x': float(abs_x),
        'y': float(abs_y),
        'area': float(area),
        'confidence': float(confidence),
        'found': True
    }

def main():
    ap = argparse.ArgumentParser(description="Step 1: Find anchor marks")
    ap.add_argument("--run-dir", required=True, help="Run directory with images/")
    ap.add_argument("--template", required=True, help="Template JSON with anchor positions")
    ap.add_argument("--search-window", type=int, default=80, help="Search window size in pixels")
    args = ap.parse_args()
    
    run_dir = pathlib.Path(args.run_dir)
    images_dir = run_dir / "step0_images"
    
    # Create step1 output directory
    step1_dir = run_dir / "step1_anchor_detection"
    step1_dir.mkdir(exist_ok=True)
    visualizations_dir = step1_dir / "visualizations"
    visualizations_dir.mkdir(exist_ok=True)
    
    # Load template
    with open(args.template) as f:
        template = json.load(f)
    
    anchors_norm = template['anchors_norm']
    
    print("=" * 80)
    print("STEP 1: ANCHOR DETECTION")
    print("=" * 80)
    print(f"Run directory: {run_dir}")
    print(f"Template: {args.template}")
    print(f"Expected anchors: {len(anchors_norm)}")
    print(f"Search window: ±{args.search_window}px")
    print()
    
    # Process each page
    pages = sorted(images_dir.glob("page_*.png"))
    if not pages:
        print("❌ No page_*.png files found!")
        return
    
    print(f"Processing {len(pages)} pages...\n")
    
    results = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'template': args.template,
        'search_window': args.search_window,
        'expected_anchors': anchors_norm,
        'pages': {}
    }
    
    for img_path in pages:
        print(f"📄 {img_path.name}")
        
        # Load image
        img = cv2.imread(str(img_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape[:2]
        
        print(f"   Image size: {w}×{h} pixels")
        
        # Calculate expected anchor positions in pixels
        expected_positions = [
            (w * a['x'], h * a['y']) for a in anchors_norm
        ]
        
        # Detect anchors
        detected = []
        for i, (exp_x, exp_y) in enumerate(expected_positions):
            corner_name = ["Top-Left", "Top-Right", "Bottom-Right", "Bottom-Left"][i]
            print(f"   Anchor {i+1} ({corner_name}):")
            print(f"      Expected: ({exp_x:.1f}, {exp_y:.1f})")
            
            result = find_l_marks(gray, (exp_x, exp_y), args.search_window)
            
            if result:
                print(f"      ✓ Detected: ({result['x']:.1f}, {result['y']:.1f})")
                print(f"      Confidence: {result['confidence']:.2%}")
                print(f"      Area: {result['area']:.0f} px²")
                detected.append(result)
            else:
                print(f"      ✗ NOT FOUND")
                detected.append({
                    'x': exp_x,
                    'y': exp_y,
                    'found': False,
                    'confidence': 0.0
                })
        
        # Calculate detection rate
        found_count = sum(1 for d in detected if d.get('found', False))
        detection_rate = found_count / len(anchors_norm)
        
        print(f"   Detection: {found_count}/{len(anchors_norm)} anchors ({detection_rate:.0%})")
        
        # Create visualization
        vis_img = img.copy()
        for i, (anchor_data, (exp_x, exp_y)) in enumerate(zip(detected, expected_positions)):
            corner_name = ["TL", "TR", "BR", "BL"][i]
            
            if anchor_data.get('found', False):
                # Draw detected anchor (green)
                det_x, det_y = int(anchor_data['x']), int(anchor_data['y'])
                cv2.circle(vis_img, (det_x, det_y), 15, (0, 255, 0), 3)
                cv2.putText(vis_img, f"{corner_name}", (det_x+20, det_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Draw search area (light green)
                cv2.rectangle(vis_img, 
                            (int(exp_x - args.search_window), int(exp_y - args.search_window)),
                            (int(exp_x + args.search_window), int(exp_y + args.search_window)),
                            (0, 255, 0), 1)
            else:
                # Draw expected position (red)
                exp_xi, exp_yi = int(exp_x), int(exp_y)
                cv2.circle(vis_img, (exp_xi, exp_yi), 15, (0, 0, 255), 3)
                cv2.putText(vis_img, f"{corner_name} ?", (exp_xi+20, exp_yi), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Draw search area (red)
                cv2.rectangle(vis_img, 
                            (int(exp_x - args.search_window), int(exp_y - args.search_window)),
                            (int(exp_x + args.search_window), int(exp_y + args.search_window)),
                            (0, 0, 255), 1)
        
        # Add legend
        cv2.putText(vis_img, f"Anchors: {found_count}/{len(anchors_norm)}", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(vis_img, "Green = Detected | Red = Not Found", 
                   (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Save visualization
        vis_path = visualizations_dir / f"{img_path.stem}_anchors.png"
        cv2.imwrite(str(vis_path), vis_img)
        
        # Store results
        results['pages'][img_path.name] = {
            'image_size': {'width': w, 'height': h},
            'detected_anchors': detected,
            'detection_rate': detection_rate,
            'found_count': found_count
        }
        
        print()
    
    # Save detailed JSON log
    log_path = step1_dir / "anchor_detection_log.json"
    with open(log_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    total_anchors = len(pages) * len(anchors_norm)
    total_found = sum(r['found_count'] for r in results['pages'].values())
    overall_rate = total_found / total_anchors if total_anchors > 0 else 0
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total pages: {len(pages)}")
    print(f"Total anchors expected: {total_anchors}")
    print(f"Total anchors detected: {total_found}")
    print(f"Overall detection rate: {overall_rate:.1%}")
    print(f"\n✅ Logs saved to: {step1_dir}")
    print(f"✅ Visualizations: {visualizations_dir}")
    print(f"✅ JSON log: {log_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
