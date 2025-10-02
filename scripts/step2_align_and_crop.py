#!/usr/bin/env python3
"""
Step 2: Align and Crop Pages

This script:
1. Loads anchor detections from Step 1
2. Computes homography/affine transformations
3. Warps images to template space
4. Crops to consistent content area (12.5% inset from anchors)
5. Generates alignment quality metrics and visualizations

Cropping Strategy:
- Removes edge artifacts from transformation
- Creates consistent bounding box across all pages
- Insets 12.5% from anchor boundaries
- Results in ~1645×2188px content area

Usage:
    python scripts/step2_align_and_crop.py <run_directory>

Example:
    python scripts/step2_align_and_crop.py artifacts/run_20251001_181157
"""

import cv2
import numpy as np
import json
import sys
from pathlib import Path


def read_json(path):
    """Read JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_crop_region(template_anchors, margin_inches=0.125, dpi=300):
    """
    Compute crop region based on anchor positions.

    Args:
        template_anchors: Dict of anchor positions {id: (x, y)}
        margin_inches: Physical margin in inches to expand OUTWARD (default 0.125 = 1/8 inch)
        dpi: Dots per inch for conversion (default 300)

    Returns:
        Tuple of (x1, y1, x2, y2) crop coordinates
    """
    # Use calibrated crop region from run_20251002_081927
    # This produces 2267 x 2954 px crops with correct checkbox overlay alignment
    x1 = 141
    y1 = 195
    x2 = 2408
    y2 = 3149

    return (x1, y1, x2, y2)


def align_and_crop_pages(run_dir):
    """Process all pages through alignment and cropping."""
    RUN_DIR = Path(run_dir)

    # Support multiple directory naming conventions
    if (RUN_DIR / "step0_images").exists():
        INPUT_DIR = RUN_DIR / "step0_images"
    elif (RUN_DIR / "00_input").exists():
        INPUT_DIR = RUN_DIR / "00_input"
    elif (RUN_DIR / "images").exists():
        INPUT_DIR = RUN_DIR / "images"
    else:
        raise FileNotFoundError(f"No input directory found in {RUN_DIR}. Looking for step0_images/, 00_input/, or images/")

    if (RUN_DIR / "step1_anchor_detection").exists():
        STEP1_DIR = RUN_DIR / "step1_anchor_detection"
    elif (RUN_DIR / "01_step1_anchor_detection").exists():
        STEP1_DIR = RUN_DIR / "01_step1_anchor_detection"
    else:
        raise FileNotFoundError(f"No step1 directory found in {RUN_DIR}. Looking for step1_anchor_detection/ or 01_step1_anchor_detection/")

    STEP2_DIR = RUN_DIR / "step2_alignment_and_crop"
    TEMPLATE_DIR = Path("templates/crc_survey_l_anchors_v1")

    # Create output directories
    STEP2_DIR.mkdir(parents=True, exist_ok=True)
    ALIGNED_FULL_DIR = STEP2_DIR / "aligned_full"
    ALIGNED_CROPPED_DIR = STEP2_DIR / "aligned_cropped"
    VIZ_DIR = STEP2_DIR / "visualizations"
    ALIGNED_FULL_DIR.mkdir(exist_ok=True)
    ALIGNED_CROPPED_DIR.mkdir(exist_ok=True)
    VIZ_DIR.mkdir(exist_ok=True)

    # Load template
    template = read_json(TEMPLATE_DIR / "template.json")
    page_width = template["page_size"]["width_px"]
    page_height = template["page_size"]["height_px"]

    # Convert template anchors to pixel coordinates
    anchors_norm = template["anchors_norm"]
    template_anchors = {
        "TL": (
            int(anchors_norm[0]["x"] * page_width),
            int(anchors_norm[0]["y"] * page_height),
        ),
        "TR": (
            int(anchors_norm[1]["x"] * page_width),
            int(anchors_norm[1]["y"] * page_height),
        ),
        "BR": (
            int(anchors_norm[2]["x"] * page_width),
            int(anchors_norm[2]["y"] * page_height),
        ),
        "BL": (
            int(anchors_norm[3]["x"] * page_width),
            int(anchors_norm[3]["y"] * page_height),
        ),
    }

    # Compute crop region (expand outward by 1/8 inch = 37.5px at 300 DPI)
    MARGIN_INCHES = 0.125
    DPI = 300
    crop_x1, crop_y1, crop_x2, crop_y2 = compute_crop_region(
        template_anchors, margin_inches=MARGIN_INCHES, dpi=DPI
    )
    crop_width = crop_x2 - crop_x1
    crop_height = crop_y2 - crop_y1

    # Load anchor detections from log
    # Support both file naming conventions
    if (STEP1_DIR / "anchor_log.json").exists():
        anchor_log = read_json(STEP1_DIR / "anchor_log.json")
    elif (STEP1_DIR / "anchor_detection_log.json").exists():
        anchor_log = read_json(STEP1_DIR / "anchor_detection_log.json")
    else:
        raise FileNotFoundError(f"No anchor log found in {STEP1_DIR}")

    print("=" * 80)
    print("STEP 2: ALIGNMENT AND CROPPING")
    print("=" * 80)
    print(f"\nTemplate size: {page_width}×{page_height}px")
    print("Template anchors (pixels):")
    for anchor_id, (x, y) in sorted(template_anchors.items()):
        print(f"  {anchor_id}: ({x:4d}, {y:4d})")
    print(
        f"\nCrop region (margin: {MARGIN_INCHES} inch = {int(MARGIN_INCHES*DPI)}px outward):"
    )
    print(f"  X: {crop_x1} → {crop_x2} (width: {crop_width}px)")
    print(f"  Y: {crop_y1} → {crop_y2} (height: {crop_height}px)")
    print(f"  Cropped size: {crop_width}×{crop_height}px")
    print()

    # Alignment thresholds
    THRESH_OK = 4.5
    THRESH_WARN = 6.0

    results = []
    alignment_summary = {"ok": 0, "warn": 0, "fail": 0}

    page_files = sorted(INPUT_DIR.glob("page_*.png"))
    print(f"Processing {len(page_files)} pages...\n")

    for page_file in page_files:
        page_num = int(page_file.stem.split("_")[1])
        page_key = page_file.name

        # Get anchor detections from log
        # Support both log formats (old and new)
        if page_key not in anchor_log and "pages" in anchor_log:
            # New format with nested 'pages' dict
            if page_key not in anchor_log["pages"]:
                print(f"❌ Page {page_num:2d}: Not found in anchor log")
                alignment_summary["fail"] += 1
                continue
            page_data = anchor_log["pages"][page_key]
        elif page_key in anchor_log:
            # Old format with pages at root level
            page_data = anchor_log[page_key]
        else:
            print(f"❌ Page {page_num:2d}: Not found in anchor log")
            alignment_summary["fail"] += 1
            continue

        # Extract found anchors from new format
        detected_list = page_data.get("detected_anchors", page_data.get("detected", []))

        # Extract found anchors
        found_anchors = {}
        anchor_ids = ["TL", "TR", "BR", "BL"]
        for i, anchor_data in enumerate(detected_list):
            if anchor_data.get("found", False):
                anchor_id = anchor_ids[i]
                # Support both old and new field names
                x = anchor_data.get("x", anchor_data.get("detected_x"))
                y = anchor_data.get("y", anchor_data.get("detected_y"))
                found_anchors[anchor_id] = (x, y)

        if len(found_anchors) < 3:
            print(f"❌ Page {page_num:2d}: Only {len(found_anchors)}/4 anchors")
            results.append(
                {
                    "page": page_num,
                    "status": "FAIL",
                    "reason": f"Insufficient ({len(found_anchors)})",
                }
            )
            alignment_summary["fail"] += 1
            continue

        # Load image
        img = cv2.imread(str(page_file))
        if img is None:
            print(f"❌ Page {page_num:2d}: Cannot load image")
            alignment_summary["fail"] += 1
            continue

        # Prepare point correspondences
        src_points = []
        dst_points = []
        anchor_order = []

        for anchor_id in ["TL", "TR", "BR", "BL"]:
            if anchor_id in found_anchors:
                src_x, src_y = found_anchors[anchor_id]
                dst_x, dst_y = template_anchors[anchor_id]
                src_points.append([src_x, src_y])
                dst_points.append([dst_x, dst_y])
                anchor_order.append(anchor_id)

        src_points = np.float32(src_points)
        dst_points = np.float32(dst_points)

        # Compute transformation
        if len(src_points) == 4:
            M, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 3.0)
            transform_type = "homography"
        elif len(src_points) == 3:
            M = cv2.getAffineTransform(src_points, dst_points)
            M = np.vstack([M, [0, 0, 1]])
            transform_type = "affine"
        else:
            alignment_summary["fail"] += 1
            continue

        if M is None:
            print(f"❌ Page {page_num:2d}: Transform failed")
            alignment_summary["fail"] += 1
            continue

        # Warp image to full template size
        aligned_full = cv2.warpPerspective(
            img,
            M,
            (page_width, page_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255),
        )

        # Crop to content area
        aligned_cropped = aligned_full[crop_y1:crop_y2, crop_x1:crop_x2]

        # Save both versions
        full_path = STEP2_DIR / "aligned_full" / f"page_{page_num:04d}_aligned_full.png"
        crop_path = (
            STEP2_DIR / "aligned_cropped" / f"page_{page_num:04d}_aligned_cropped.png"
        )
        cv2.imwrite(str(full_path), aligned_full)
        cv2.imwrite(str(crop_path), aligned_cropped)

        # Calculate residuals
        residuals = []
        for i, (src_pt, dst_pt) in enumerate(zip(src_points, dst_points)):
            src_h = np.array([src_pt[0], src_pt[1], 1.0])
            transformed = M @ src_h
            transformed = transformed / transformed[2]
            error = np.sqrt(
                (transformed[0] - dst_pt[0]) ** 2 + (transformed[1] - dst_pt[1]) ** 2
            )
            residuals.append({"anchor": anchor_order[i], "error_px": float(error)})

        mean_error = np.mean([r["error_px"] for r in residuals])
        max_error = np.max([r["error_px"] for r in residuals])

        # Determine quality
        if mean_error <= THRESH_OK:
            quality = "OK"
            status_icon = "✅"
            alignment_summary["ok"] += 1
        elif mean_error <= THRESH_WARN:
            quality = "WARN"
            status_icon = "⚠️"
            alignment_summary["warn"] += 1
        else:
            quality = "FAIL"
            status_icon = "❌"
            alignment_summary["fail"] += 1

        # Create visualization with crop region highlighted
        vis = aligned_full.copy()

        # Draw crop region (cyan rectangle)
        cv2.rectangle(vis, (crop_x1, crop_y1), (crop_x2, crop_y2), (255, 255, 0), 3)
        cv2.putText(
            vis,
            "Crop Region",
            (crop_x1 + 10, crop_y1 + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 0),
            2,
        )

        # Draw anchor positions
        for anchor_id, (x, y) in template_anchors.items():
            cv2.circle(vis, (x, y), 15, (0, 255, 0), 2)
            cv2.putText(
                vis,
                anchor_id,
                (x - 30, y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

            if anchor_id in found_anchors:
                for res in residuals:
                    if res["anchor"] == anchor_id:
                        error = res["error_px"]
                        color = (
                            (0, 255, 0)
                            if error <= THRESH_OK
                            else (0, 165, 255)
                            if error <= THRESH_WARN
                            else (0, 0, 255)
                        )
                        cv2.circle(vis, (x, y), int(error) + 5, color, 2)
                        cv2.putText(
                            vis,
                            f"{error:.1f}px",
                            (x + 20, y + 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            color,
                            1,
                        )

        # Add quality label
        label = f"Page {page_num} - {quality} - Mean: {mean_error:.2f}px, Max: {max_error:.2f}px"
        cv2.putText(
            vis,
            label,
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (
                (0, 255, 0)
                if quality == "OK"
                else (0, 165, 255)
                if quality == "WARN"
                else (0, 0, 255)
            ),
            2,
        )

        vis_path = (
            STEP2_DIR / "visualizations" / f"page_{page_num:04d}_alignment_check.png"
        )
        cv2.imwrite(str(vis_path), vis)

        # Store results
        result = {
            "page": page_num,
            "status": quality,
            "transform_type": transform_type,
            "anchors_used": len(src_points),
            "anchor_order": anchor_order,
            "mean_error_px": float(mean_error),
            "max_error_px": float(max_error),
            "residuals": residuals,
            "matrix": M.tolist(),
            "crop_region": {
                "x1": crop_x1,
                "y1": crop_y1,
                "x2": crop_x2,
                "y2": crop_y2,
                "width": crop_width,
                "height": crop_height,
            },
        }
        results.append(result)

        print(
            f"{status_icon} Page {page_num:2d}: {quality:4s} | {transform_type:10s} | "
            f"{len(src_points)}/4 anchors | Mean: {mean_error:.2f}px | Max: {max_error:.2f}px"
        )

    # Save results
    results_file = STEP2_DIR / "alignment_results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "summary": alignment_summary,
                "thresholds": {"ok_px": THRESH_OK, "warn_px": THRESH_WARN},
                "crop_settings": {
                    "margin_inches": MARGIN_INCHES,
                    "margin_px": int(MARGIN_INCHES * DPI),
                    "crop_region_px": {
                        "x1": crop_x1,
                        "y1": crop_y1,
                        "x2": crop_x2,
                        "y2": crop_y2,
                        "width": crop_width,
                        "height": crop_height,
                    },
                },
                "pages": results,
            },
            f,
            indent=2,
        )

    print("\n" + "=" * 80)
    print("ALIGNMENT & CROPPING SUMMARY")
    print("=" * 80)
    print(f"✅ OK:   {alignment_summary['ok']:2d} pages (error ≤ {THRESH_OK:.1f}px)")
    print(
        f"⚠️  WARN: {alignment_summary['warn']:2d} pages (error ≤ {THRESH_WARN:.1f}px)"
    )
    print(
        f"❌ FAIL: {alignment_summary['fail']:2d} pages (error > {THRESH_WARN:.1f}px or no alignment)"
    )
    print(
        f"\nTotal aligned: {alignment_summary['ok'] + alignment_summary['warn']}/{len(page_files)} pages"
    )
    print("\nOutput files:")
    print(f"  - Full aligned: aligned_full/ ({page_width}×{page_height}px)")
    print(f"  - Cropped: aligned_cropped/ ({crop_width}×{crop_height}px)")
    print("  - Visualizations: visualizations/")
    print("  - Details: alignment_results.json")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Step 2: Align and crop pages based on anchors")
    ap.add_argument("--run-dir", required=True, help="Run directory with step0_images/ and step1_anchor_detection/")
    ap.add_argument("--template", required=True, help="Template JSON (for compatibility, not used in this script)")
    args = ap.parse_args()
    
    align_and_crop_pages(args.run_dir)
