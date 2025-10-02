#!/usr/bin/env python3
"""
STEP 2: Align pages using detected anchors
- Computes homography transformation from detected anchors
- Calculates alignment quality (residuals)
- Warps pages to template space
- Creates aligned page images
"""
import argparse
import json
import pathlib
import time
import numpy as np
import cv2


def compute_homography(src_points, dst_points, ransac_threshold=3.0):
    """
    Compute homography matrix from source to destination points.
    Returns: (M, Minv, residuals, quality)
    """
    src = np.float32(src_points)
    dst = np.float32(dst_points)
    
    # Compute homography with RANSAC
    M, mask = cv2.findHomography(src, dst, cv2.RANSAC, ransac_threshold)
    
    if M is None or not np.all(np.isfinite(M)):
        # Fallback to simple scaling if homography fails
        print("      ⚠️  Homography failed, using simple scaling")
        src_h, src_w = np.max(src, axis=0)
        dst_h, dst_w = np.max(dst, axis=0)
        sx, sy = dst_w / src_w, dst_h / src_h
        M = np.float32([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
        mask = np.ones(len(src), dtype=np.uint8)
    
    # Calculate inverse
    Minv = np.linalg.inv(M)
    
    # Calculate residuals (reprojection error)
    residuals = []
    for i, (s, d) in enumerate(zip(src, dst)):
        # Transform source point
        transformed = M @ np.array([s[0], s[1], 1.0])
        transformed = transformed[:2] / transformed[2]
        
        # Calculate error
        error = np.linalg.norm(transformed - d)
        residuals.append(float(error))
    
    avg_residual = np.mean(residuals)
    max_residual = np.max(residuals)
    
    return M, Minv, residuals, avg_residual, max_residual


def main():
    ap = argparse.ArgumentParser(description="Step 2: Align pages using anchors")
    ap.add_argument("--run-dir", required=True, help="Run directory")
    ap.add_argument("--template", required=True, help="Template JSON")
    ap.add_argument("--ransac-threshold", type=float, default=3.0, help="RANSAC threshold in pixels")
    ap.add_argument("--warn-threshold", type=float, default=4.5, help="Warning residual threshold")
    ap.add_argument("--fail-threshold", type=float, default=6.0, help="Failure residual threshold")
    args = ap.parse_args()
    
    run_dir = pathlib.Path(args.run_dir)
    images_dir = run_dir / "step0_images"
    step1_dir = run_dir / "step1_anchor_detection"
    
    # Create step2 output directory
    step2_dir = run_dir / "step2_alignment_and_crop"
    step2_dir.mkdir(exist_ok=True)
    aligned_dir = step2_dir / "aligned_full"
    aligned_dir.mkdir(exist_ok=True)
    cropped_dir = step2_dir / "aligned_cropped"
    cropped_dir.mkdir(exist_ok=True)
    
    # Load template
    with open(args.template) as f:
        template = json.load(f)
    
    page_size = template.get('page_size', {'width_px': 2550, 'height_px': 3300})
    tpl_w, tpl_h = int(page_size['width_px']), int(page_size['height_px'])
    anchors_norm = template['anchors_norm']
    
    # Load anchor detection results
    anchor_log = step1_dir / "anchor_detection_log.json"
    if not anchor_log.exists():
        print(f"❌ Step 1 results not found: {anchor_log}")
        print("   Run step1_find_anchors.py first!")
        return
    
    with open(anchor_log) as f:
        anchor_data = json.load(f)
    
    print("=" * 80)
    print("STEP 2: PAGE ALIGNMENT")
    print("=" * 80)
    print(f"Run directory: {run_dir}")
    print(f"Template size: {tpl_w}×{tpl_h} pixels")
    print(f"RANSAC threshold: {args.ransac_threshold} px")
    print(f"Quality thresholds: OK ≤ {args.warn_threshold}px, WARN ≤ {args.fail_threshold}px")
    print()
    
    # Template anchor positions (destination)
    dst_points = [[tpl_w * a['x'], tpl_h * a['y']] for a in anchors_norm]
    
    results = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'template_size': {'width': tpl_w, 'height': tpl_h},
        'thresholds': {
            'ransac': args.ransac_threshold,
            'warn_px': args.warn_threshold,
            'fail_px': args.fail_threshold
        },
        'pages': {}
    }
    
    quality_counts = {'ok': 0, 'warn': 0, 'fail': 0}
    
    # Process each page
    for page_name, page_data in sorted(anchor_data['pages'].items()):
        print(f"📄 {page_name}")
        
        # Get detected anchor positions (source)
        detected_anchors = page_data['detected_anchors']
        src_points = [[a['x'], a['y']] for a in detected_anchors]
        
        # Check if all anchors were found
        found_count = sum(1 for a in detected_anchors if a.get('found', False))
        print(f"   Anchors found: {found_count}/{len(anchors_norm)}")
        
        # Compute homography
        M, Minv, residuals, avg_residual, max_residual = compute_homography(
            src_points, dst_points, args.ransac_threshold
        )
        
        # Determine quality
        if avg_residual <= args.warn_threshold:
            quality = 'ok'
            icon = '✅'
        elif avg_residual <= args.fail_threshold:
            quality = 'warn'
            icon = '⚠️'
        else:
            quality = 'fail'
            icon = '❌'
        
        quality_counts[quality] += 1
        
        print(f"   {icon} Average residual: {avg_residual:.3f} px")
        print(f"   Max residual: {max_residual:.3f} px")
        print(f"   Quality: {quality.upper()}")
        
        # Show individual anchor residuals
        for i, (res, anchor) in enumerate(zip(residuals, detected_anchors)):
            corner = ["TL", "TR", "BR", "BL"][i]
            found_str = "✓" if anchor.get('found', False) else "✗"
            print(f"      {corner}: {res:.3f} px {found_str}")
        
        # Warp image to template space
        img_path = images_dir / page_name
        img = cv2.imread(str(img_path))
        
        if img is not None:
            # Warp to template space
            aligned = cv2.warpPerspective(img, M, (tpl_w, tpl_h))
            
            # Save aligned image
            aligned_path = aligned_dir / page_name
            cv2.imwrite(str(aligned_path), aligned)
            print(f"   💾 Saved aligned: {aligned_path.name}")
        
        # Store results
        results['pages'][page_name] = {
            'homography_matrix': M.tolist(),
            'inverse_matrix': Minv.tolist(),
            'residuals': residuals,
            'avg_residual_px': float(avg_residual),
            'max_residual_px': float(max_residual),
            'quality': quality,
            'anchors_found': found_count,
            'anchors_total': len(anchors_norm)
        }
        
        print()
    
    # Save alignment results
    log_path = step2_dir / "alignment_log.json"
    with open(log_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    total_pages = len(results['pages'])
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total pages processed: {total_pages}")
    print(f"\nAlignment Quality:")
    print(f"  ✅ OK:   {quality_counts['ok']} pages ({quality_counts['ok']/total_pages*100:.1f}%)")
    print(f"  ⚠️  WARN: {quality_counts['warn']} pages ({quality_counts['warn']/total_pages*100:.1f}%)")
    print(f"  ❌ FAIL: {quality_counts['fail']} pages ({quality_counts['fail']/total_pages*100:.1f}%)")
    
    # Calculate average residuals
    all_residuals = [p['avg_residual_px'] for p in results['pages'].values()]
    if all_residuals:
        print(f"\nResidual Statistics:")
        print(f"  Average: {np.mean(all_residuals):.3f} px")
        print(f"  Min: {np.min(all_residuals):.3f} px")
        print(f"  Max: {np.max(all_residuals):.3f} px")
    
    print(f"\n✅ Logs saved to: {step2_dir}")
    print(f"✅ Aligned images: {aligned_dir}")
    print(f"✅ JSON log: {log_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
